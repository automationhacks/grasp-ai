import asyncio
from contextlib import AsyncExitStack
import os

from agent_framework import Agent, tool
from agent_framework_foundry import FoundryChatClient
from agent_framework_hyperlight import HyperlightCodeActProvider
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

"""
As of writing this, this code sample can only work on linux or windows
as hyperlight is not supported on mac yet.
"""


@tool
def compute(operation: str, a: float, b: float) -> float:
    """Perform a math operation"""
    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b
    }

    return ops[operation]


codeact = HyperlightCodeActProvider(
    tools=[compute],
    approval_mode="never_require"
)


async def main():
    load_dotenv()
    PROJECT_PROJECT_ENDPOINT = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
    FOUNDRY_MODEL = os.environ.get("FOUNDRY_MODEL")

    client = FoundryChatClient(credential=AzureCliCredential())

    agent = Agent(
        client=client,
        name="CodeActAgent",
        instructions="You are a helpful assistant.",
        context_providers=[codeact],
    )

    async with AsyncExitStack() as stack:
        result = await agent.run("Multiply 6 by 7 using execute_code.")


if __name__ == '__main__':
    asyncio.run(main())
