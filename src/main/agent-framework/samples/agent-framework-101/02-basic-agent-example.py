import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential()
)

# Create an Agent with a model and instructions
agent = project.agents.create_version(
    agent_name="basic-agent-01",
    definition=PromptAgentDefinition(
        model="gpt-5.4-mini",
        instructions="""
        You are a helpful assistant that answers questions about any topic.""",
    ),
)
print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
