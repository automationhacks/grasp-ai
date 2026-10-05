import asyncio
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    # Initialize a Chat client for a model hosted in foundry
    client = FoundryChatClient(
        project_endpoint=os.environ.get("FOUNDRY_PROJECT_ENDPOINT"),
        model=os.environ.get("FOUNDRY_MODEL"),
        credential=AzureCliCredential(),
    )

    # Create an Agent with the above client
    # The agent class has options to configure different features like memory, background agents, tools etc
    agent = Agent(
        client=client,
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep your answers brief."
    )

    # This gives the entire answer without streaming it
    result = await agent.run("What is the capital of India?")
    print(f"Agent: {result}")

    # This will stream the answer on the terminal
    print("Agent (streaming): ", end="", flush=True)
    prompt = "Tell me a one sentence fun fact."
    # The streaming behavior comes from using stream=True in run()
    async for chunk in agent.run(prompt, stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
