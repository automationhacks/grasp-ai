"""
This file follows tutorial from agent-framework on building your own agent with harness

Tutorial blog: https://devblogs.microsoft.com/agent-framework/agent-harness-scaling-the-claw-or-harness-capabilities/
Github sample: https://github.com/microsoft/agent-framework/blob/main/python/samples/02-agents/harness/build_your_own_claw/claw_step03_scaling_capabilities.py

It also makes use of console which is a terminal UI (TUI)
https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/harness/console
"""

import asyncio
from collections.abc import Callable, Generator
from contextlib import AsyncExitStack
import importlib
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Literal
from uuid import uuid4

from agents import LocalShellTool, ShellPolicy
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import subprocess_script_runner

from agent_framework import (
    AgentModeProvider,
    Content,
    FileAccessProvider,
    FileSkillsSource,
    FileSystemAgentFileStore,
    MCPSkillsSource,
    create_harness_agent,
    tool,
    SkillsProvider,
    SkillsSource,
    AggregatingSkillsSource,
    DeduplicatingSkillsSource,
    MCPSkillResource
)
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry import FoundryMemoryProvider
from azure.identity import AzureCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from pydantic import Field

# Reuse the shared harness console from a local agent-framework repo checkout.
DEFAULT_HARNESS_DIR = (
    Path.home()
    / "self"
    / "agent-framework"
    / "python"
    / "samples"
    / "02-agents"
    / "harness"
)
_SAMPLE_DIR = Path(__file__).resolve().parent
_WORKING_DIR = _SAMPLE_DIR / "working"
_VAULT_DIR = _WORKING_DIR / "confirmations"
_SKILLS_DIR = _SAMPLE_DIR / "skills"
_MEMORY_SCOPE = "agent-harness-sample-user"

# we are reusing the harness from agent-framework repo which should be also cloned.
# please read the README.md file src/main/agent-framework/samples/agent-framework-101/README.md
# for instructions
HARNESS_DIR = Path(
    os.environ.get("AGENT_FRAMEWORK_HARNESS_DIR", str(DEFAULT_HARNESS_DIR))
).expanduser()
if HARNESS_DIR.exists():
    sys.path.insert(0, str(HARNESS_DIR))
else:
    raise RuntimeError(
        "Harness directory not found. Set AGENT_FRAMEWORK_HARNESS_DIR to "
        "<agent-framework>/python/samples/02-agents/harness"
    )

console_module = importlib.import_module("console")
build_observers_with_planning = console_module.build_observers_with_planning
run_agent_async = console_module.run_agent_async

# Config
PROJECT_PROJECT_ENDPOINT = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_MODEL = os.environ.get("FOUNDRY_MODEL")

# instructions
FINANCE_INSTRUCTIONS = """\
## Personal Finance Assistant Instructions

You are a personal finance and investing assistant. You help the user understand their portfolio
and watchlist, and you can place trades on their behalf.

### Working style

- The user's holdings live in a file called portfolio.csv. Read it with the file_access tools
  before answering questions about their portfolio, and never modify it unless asked.
- When asked for a report or analysis, write it to a Markdown file with the file_access tools
  (e.g. reports/portfolio-review.md) and tell the user where you saved it.
- Keep the user's watchlist in a memory file called watchlist.md: read it when reviewing the
  watchlist, and update it whenever the user adds or removes a ticker.
- To buy or sell, use the place_trade tool. This takes a real action, so the user will be asked to
  approve it before it runs — explain what you are about to do first.
- Remember durable facts the user tells you about themselves (risk tolerance, goals, preferences)
  and take them into account when giving analysis.

### Important

You provide information and analysis only — you are not a licensed financial advisor and you must
not present your output as personalized investment advice. Remind the user to do their own
research before making decisions.
"""

# constants
_PRICE_BOOK: dict[str, float] = {
    "MSFT": 462.97,
    "AAPL": 229.35,
    "GOOGL": 178.12,
    "AMZN": 201.45,
    "NVDA": 134.81,
}


# tools
def get_stock_price(
    symbol: Annotated[str, "The stock ticker symbol, e.g. MSFT or AAPL."],
) -> dict[str, object]:
    """
    Get the latest (delayed, illustrative) stock price for a ticker symbol.
    """
    ticker = symbol.upper()
    price = _PRICE_BOOK.get(ticker)

    if not price:
        price = random.uniform(100.10, 500.99)
    return {
        "symbol": ticker,
        "price": round(price, 2),
        "currency": "USD",
        "as_of": datetime.now(timezone.utc).isoformat(),
    }


@tool(approval_mode="always_require")
def place_trade(
    symbol: Annotated[str, "Stock ticker symbol to trade. e.g. MSFT"],
    action: Annotated[Literal["buy", "sell"], "Either 'buy' or 'sell'"],
    quantity: Annotated[int, Field(gt=0, description="The number of shares to trade")],
):
    verb = "Sold" if action == "sell" else "Bought"
    confirmation = f"TRADE-{uuid4().hex[:8].upper()}"
    return f"{verb} {quantity} shares of {symbol.upper()}. Confirmation: {confirmation}"


# auto approval rules
async def auto_approve_small_trades(call: Content) -> bool:
    if call.name != "place_trade":
        return False

    args = call.parse_arguments() or {}
    symbol = str(args.get("symbol", "")).upper()
    if not symbol:
        return False

    qty_raw = args.get("quantity", 0)
    try:
        qty = int(qty_raw)
    except (TypeError, ValueError):
        return False

    price_data = get_stock_price(symbol)
    price = float(price_data.get("price", 0.0))
    estimate = qty * price
    # A trade less than $1000 can be auto approved.
    return estimate < 1000


async def _enable_foundry_memory(stack: AsyncExitStack) -> FoundryMemoryProvider | None:
    endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
    store_name = os.environ.get("FOUNDRY_MEMORY_STORE")
    embedding_model = os.environ.get("FOUNDRY_EMBEDDING_MODEL")
    chat_model = os.environ.get("FOUNDRY_MODEL", "gpt-5.4")

    if not (endpoint and store_name and embedding_model):
        print("Foundry memory disabled. Set FOUNDRY_MEMORY_STORE and FOUNDRY_EMBEDDING_MODEL to enable it")
        return None

    from azure.ai.projects.aio import AIProjectClient
    from azure.ai.projects.models import MemoryStoreDefaultDefinition, MemoryStoreDefaultOptions
    from azure.core.exceptions import ResourceNotFoundError
    from azure.identity.aio import AzureCliCredential as AsyncAzureCliCredential

    credential = await stack.enter_async_context(AzureCliCredential())
    project_client = await stack.enter_async_context(AIProjectClient(endpoint=endpoint, credential=credential))

    try:
        await project_client.beta.memory_stores.get(name=store_name)
        print(f"Using existing memory store '{store_name}'")
    except ResourceNotFoundError:
        definition = MemoryStoreDefaultDefinition(
            chat_model=chat_model,
            embedding_model=embedding_model,
            options=MemoryStoreDefaultOptions(
                chat_summary_enabled=False, user_profile_enabled=True)
        )
        await project_client.beta.memory_stores.create(
            name=store_name,
            embedding_model=embedding_model,
            options=MemoryStoreDefaultOptions(
                chat_summary_enabled=False, user_profile_details=True)
        )
    provider = FoundryMemoryProvider(
        project_client=project_client,
        memory_store_name=store_name,
        scope=_MEMORY_SCOPE,
        # In production, memories should be batched with delay.
        update_delay=0
    )
    print(f"Foundry memory enabled (store: {store_name})")
    return provider


async def _build_skills_provider(stack: AsyncExitStack) -> SkillsProvider:
    """
    Builds a skill provider over local skills/ folder, or optional Foundry managed skills

    File based skills always load. When FOUNDRY_TOOLBOX_MCP_SERVER_URL is set, we
    also connect to Foundry Toolbox MCP endpoint and surface its skills, so they can be
    managed and updated centrally without changing this agent.
    """

    # subprocess_script_runner lets file based skills run their python scripts.
    sources: list[SkillsSource] = [FileSkillsSource(
        str(_SKILLS_DIR), script_runner=subprocess_script_runner)]

    toolbox_url = os.environ.get("FOUNDRY_TOOLBOX_MCP_SERVER_URL")
    if toolbox_url:
        session = await _connect_foundry_toolbox(stack, toolbox_url)
        sources.append(MCPSkillsSource(client=session))
        print("Foundry skills enabled (Toobox MCP).")
    else:
        print("Foundry skills disabled. Set FOUNDRY_TOOLBOX_MCP_SERVER_URL to enable them")

    source: SkillsSource = sources[0] if len(
        sources) == 1 else AggregatingSkillsSource(sources)
    return SkillsProvider(DeduplicatingSkillsSource(source))


async def _connect_foundry_toolbox(stack: AsyncExitStack, url: str) -> ClientSession:
    """
    Open an MCP session against Foundry Toolbox endpoint, tied to a stack's lifetime
    """
    token_provider = get_bearer_token_provider(
        AzureCliCredential(), "https://ai.azure.com/.default")
    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            auth=_ToolboxAuth(token_provider),
            headers={"Foundry-Features": "Toolboxes=V1Preview"},
            timeout=httpx.Timeout(30.0, read=300.0),
            follow_redirects=True
        )
    )

    read, write, _ = await stack.enter_async_context(streamable_http_client(url=url, http_client=http_client))
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    return session


def _build_shell() -> LocalShellTool:
    """
    A sandboxed shell, confined to trade confirmation vault

    confine_workdir re-anchors each command to the vault
    denylist prefilters any destructive command shapes
    these patterns are a UX guardrail and not a security boundry
    for hard isolation, use DockerShellTool
    Left at default approval_mode="always_require" so each command is surfaced for approval.

    """
    return LocalShellTool(mode="persistent", workdir=str(_VAULT_DIR), confine_workdir=True, policy=ShellPolicy(denylist=[
        r"\brm\s+-rf\b",
        r"\bsudo\b",
        r":\(\)\s*\{",  # fork-bomb shape
        r"\bmkfs\b",
        r">\s*/dev/sd",
    ]),
        timeout=15,)


class _ToolboxAuth(httpx.Auth):
    """Attach a fresh foundry bearer token to every request"""

    def __init__(self, token_provider: Callable[[], str]):
        self._get_token = token_provider

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self._get_token()}"
        yield request


async def main() -> None:
    load_dotenv()
    _WORKING_DIR.mkdir(exist_ok=True)

    # Setup
    client = FoundryChatClient(
        credential=AzureCliCredential(),
    )

    async with AsyncExitStack() as stack:
        skills_provider = await _build_skills_provider(stack)
        shell = _build_shell()

        context_providers: list[Any] = []
        foundry_memory = await _enable_foundry_memory(stack)
        if foundry_memory is not None:
            context_providers.append(foundry_memory)

        # Agent harness
        agent = create_harness_agent(
            client=client,
            agent_instructions=FINANCE_INSTRUCTIONS,
            tools=[get_stock_price, place_trade],
            file_access_store=FileSystemAgentFileStore(str(_WORKING_DIR)),
            auto_approval_rules=[
                FileAccessProvider.read_only_tools_auto_approval_rule,
                auto_approve_small_trades,
            ],
            context_providers=context_providers or None,
            mode_provider=AgentModeProvider(default_mode="execute"),
            skills_provider=skills_provider,
            shell_executor=shell,
        )

        session = agent.create_session()

        await run_agent_async(
            agent=agent,
            session=session,
            observers=build_observers_with_planning(agent),
            initial_mode="execute",
            title="Finance Assistant",
            placeholder="Review your portfolio, draft a report, update your watchlist, or place a trade..."
        )


if __name__ == "__main__":
    asyncio.run(main())
