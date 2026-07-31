import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
openai = project.get_openai_client(agent_name="basic-agent-01")
conversation = openai.conversations.create()

response = openai.responses.create(
    conversation=conversation.id, input="What is the size of india in km?"
)
print(response.output_text)

response = openai.responses.create(
    conversation=conversation.id, input="And what is the capital city?"
)
print(response.output_text)
