import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential()
)

agent = project.agents.create_version(
    agent_name="basic-agent",
    definition=PromptAgentDefinition(
        model="gpt-5.4-mini",
        instructions="""
        You are a helpful assistant that answers questions about Software Testing. 
        If the user asks you a question about any other topic, 
        just politely decline and tell them you can only answer questions on Testing.""",
    ),
)
print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
