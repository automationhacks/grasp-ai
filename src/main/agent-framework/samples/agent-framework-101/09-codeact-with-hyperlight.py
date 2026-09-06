from agent_framework import Agent, tool
from agent_framework_foundry import FoundryChatClient
from agent_framework_hyperlight import HyperlightCodeActProvider
from azure.identity import AzureCliCredential


@tool
def compute(operation: str, a: float, b: float) -> float:
    """Perform a math operation"""
    ops = {
        "add": a + b,
        "substract": a - b,
        "multiply": a * b,
        "divide": a / b
    }

    return ops[operation]


codeact = HyperlightCodeActProvider(
    tools=[compute],
    approval_mode="never_require"
)

client = FoundryChatClient(credential=AzureCliCredential())

agent = Agent(
    client=client,
    name="CodeActAgent",
    instructions="You are a helpful assistant.",
    context_providers=[codeact],
)

result = await agent.run("Multiply 6 by 7 using execute_code.")
