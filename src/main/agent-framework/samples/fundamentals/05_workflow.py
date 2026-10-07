import asyncio
import os
from dotenv import load_dotenv

from agent_framework import Agent, workflow
from agent_framework_foundry import FoundryChatClient
from azure.identity import AzureCliCredential


"""
Example showing how you can call agents inside workflows

Agent calls are async function calls; don't need a special wrapper.
"""
load_dotenv()
FOUNDRY_PROJECT_ENDPOINT = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_MODEL = os.environ.get("FOUNDRY_MODEL")

client = FoundryChatClient(project_endpoint=FOUNDRY_PROJECT_ENDPOINT,
                           model=FOUNDRY_MODEL, credential=AzureCliCredential())

writer_agent = Agent(
    name="WriterAgent",
    instructions="Write a short poem (4 lines max) about the given topic",
    client=client
)

reviewer_agent = Agent(
    name="ReviewerAgent",
    instructions="Review the given poem in one sentence. Is it good?",
    client=client
)


@workflow
async def poem_workflow(topic: str) -> str:
    poem = (await writer_agent.run(f"Write a poem about: {topic}")).text
    review = (await reviewer_agent.run(f"Reivew this poem {poem}")).text
    return f"Poem: \n{poem}\n\nReview: {review}"


async def main() -> None:
    workflow_instance = poem_workflow.build()
    result = await workflow_instance.run("a cat learning to code")
    print(result.get_outputs()[0])


if __name__ == '__main__':
    asyncio.run(main())
