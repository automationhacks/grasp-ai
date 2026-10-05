import asyncio
import os
from typing import Any
from agent_framework import Agent, AgentSession, ContextProvider, SessionContext
from azure.identity import AzureCliCredential
import dotenv
from agent_framework.foundry import FoundryChatClient

dotenv.load_dotenv()
FOUNDRY_PROJECT_ENDPOINT = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_MODEL = os.environ.get("FOUNDRY_MODEL")

"""
This example shows how to give your Agent memory by using ContextProvider and Session State.

Context providers inject dynamic context in each agents call. In this example we extend SessionContext by
storing the users name in session state and that personalizes the responses. Even as we do multiple turns,
we still persist the state.

Blog: https://learn.microsoft.com/en-us/agent-framework/get-started/memory?pivots=programming-language-python
"""


class UserMemoryProvider(ContextProvider):
    DEFAULT_SOURCE_ID = "user_memory"

    def __init__(self):
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(
            self,
            *,
            agent: Any,
            session: AgentSession | None,
            context: SessionContext,
            state: dict[str, Any]
    ) -> None:
        user_name = state.get("user_name")
        if user_name:
            context.extend_instructions(
                self.source_id, f"The user's name is {user_name}. Always address them by name.")
        else:
            context.extend_instructions(
                self.source_id,
                "You don't know the user's name yet. Ask them politely."
            )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any]
    ) -> None:
        """Extract and store user info in session state after each call."""
        for msg in context.input_messages:
            text = msg.text if hasattr(msg, "text") else ""
            if isinstance(text, str) and "my name is" in text.lower():
                second_half = text.lower().split("my name is")[-1]
                state["user_name"] = second_half.strip().split()[
                    0].capitalize()


async def main() -> None:
    client = FoundryChatClient(project_endpoint=FOUNDRY_PROJECT_ENDPOINT,
                               model=FOUNDRY_MODEL, credential=AzureCliCredential())
    agent = Agent(client=client, name="MemoryAgent",
                  instructions="You are a friendly assistant.", context_providers=[UserMemoryProvider()])
    session = agent.create_session()

    result = await agent.run("Hello, what is the square root of 9?", session=session)
    print(f"Agent: {result}\n")

    # Tell the agent the information about the users name
    result = await agent.run("My name is Alice", session=session)
    print(f"Agent: {result}\n")

    result = await agent.run("What is 2 + 2?", session=session)
    print(f"Agent: {result}\n")

    # Check what name is stored in session state
    provider_state = session.state.get("user_memory", {})
    print(
        f"[Session state] Stored user name: {provider_state.get('user_name')}")


if __name__ == '__main__':
    asyncio.run(main())
