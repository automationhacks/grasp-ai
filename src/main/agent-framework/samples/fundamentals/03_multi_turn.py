import asyncio
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

"""
This example shows that by using agent.create_session() and passing it in each agent invocation
we can pass the conversation history to the agent
"""


async def main() -> None:
    client = FoundryChatClient(project_endpoint=os.environ.get(
        "FOUNDRY_PROJECT_ENDPOINT"), model=os.environ.get("FOUNDRY_MODEL"), credential=AzureCliCredential())

    agent = Agent(client=client, name="ConversationAgent",
                  instructions="You are a friendly agent. Keep your answers brief")

    # with a session; we can maintain conversation history
    session = agent.create_session()

    # First turn
    result = await agent.run("My name is Gaurav and I love taking a walk in nature.", session=session)
    print(f"Agent: {result}\n")

    # Second turn
    result = await agent.run("What do you remember about me?", session=session)
    print(f"Agent: {result}")


if __name__ == '__main__':
    asyncio.run(main())
