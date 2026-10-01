import os
import asyncio
from random import randint
from typing import Annotated
from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient

from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from pydantic import Field


load_dotenv()


@tool(approval_mode="never_require")
def get_weather(location: Annotated[str, Field(description="The location to get weather for")]) -> str:
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with high of {randint(10, 30)} ˙C"


async def main() -> None:
    client = FoundryChatClient(
        project_endpoint=os.environ.get("FOUNDRY_PROJECT_ENDPOINT"),
        model=os.environ.get("FOUNDRY_MODEL",),
        credential=AzureCliCredential()
    )

    instructions = "You are a helpful weather agent. Use the get_weather tool to answer questions."
    agent = Agent(
        client=client,
        name="WeatherAgent",
        instructions=instructions,
        tools=[get_weather]
    )

    prompt = "What is the weather like in Bangalore?"
    result = await agent.run(prompt)
    print(f"Agent: {result}")


if __name__ == '__main__':
    asyncio.run(main())
