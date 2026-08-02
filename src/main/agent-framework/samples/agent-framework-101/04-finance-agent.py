"""
This file follows tutorial from agent-framework on building your own agent with harness
https://github.com/microsoft/agent-framework/blob/main/python/samples/02-agents/harness/build_your_own_claw/claw_step01_meet_your_claw.py

It also makes use of console which is a terminal UI (TUI)
https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/harness/console
"""

import asyncio
import importlib
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from agent_framework import FileSystemAgentFileStore, create_harness_agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

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

load_dotenv()
# Config
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
FOUNDRY_MODEL = os.environ.get("FOUNDRY_MODEL")

# instructions
FINANCE_INSTRUCTIONS = """\
## Personal Finance Assistant Instructions

You are a personal finance and investing assistant. When asked about a stock, look up its current
price with the get_stock_price tool, and use web search for recent news, earnings, or analyst
commentary.

### Working style
- Always verify numbers with a tool rather than relying on memory. Stock prices change.
- Cite web sources inline when you use them.
- Keep the user's watchlist in a memory file called `watchlist.md`: read it when reviewing the
  watchlist, and update it whenever the user adds or removes a ticker.

The user’s holdings live in a file called portfolio.csv. 
Read it before answering questions about their portfolio, and never modify it unless asked. 
When asked for a report, write it to a Markdown file (e.g. reports/portfolio-review.md) and 
tell the user where you saved it.
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


# Setup
client = FoundryChatClient(
    credential=AzureCliCredential(),
)

# Agent harness
agent = create_harness_agent(
    client=client,
    agent_instructions=FINANCE_INSTRUCTIONS,
    tools=[get_stock_price],
    file_access_store=FileSystemAgentFileStore("working"),
)


async def main() -> None:
    await run_agent_async(
        agent=agent,
        session=agent.create_session(),
        observers=build_observers_with_planning(agent),
        initial_mode="plan",
        title="Finance Assistant",
    )


if __name__ == "__main__":
    asyncio.run(main())
