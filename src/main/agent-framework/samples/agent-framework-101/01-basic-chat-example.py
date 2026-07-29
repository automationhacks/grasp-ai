import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME")


project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)
openai = project.get_openai_client()

responses = openai.responses.create(
    model="gpt-5.4-mini",
    input="Who created python and list the top 5 PSF members?"
)
print(f"Response output: {responses.output_text}")
