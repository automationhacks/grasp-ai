import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = "basic-chat-agent"


project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential()
)
openai = project.get_openai_client()

responses = openai.responses.create(
    model="gpt-5.4-mini",
    input="Who created python and list the the most influential people in the Python community?",
)
print(f"Response output: {responses.output_text}")
