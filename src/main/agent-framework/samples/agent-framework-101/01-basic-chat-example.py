import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# dotenv module reads any variables defined in .env files
# and then loads them as environment variables
# don't checkin .env files, they should be used to
# keep any local secrets
load_dotenv()
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = "basic-chat-agent"

# Creates a project and client to call Foundry API
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential()
)
# Creates openai client bound to the specified project
openai = project.get_openai_client()

# Create a conversation with the agent
responses = openai.responses.create(
    model="gpt-5.4-mini",
    input="Who created python and list the the most influential people in the Python community?",
)
print(f"Response output: {responses.output_text}")
