"""
Follows tutorial from Microsoft Learn
https://learn.microsoft.com/en-gb/azure/foundry/agents/how-to/tools/toolbox?pivots=python#connect-to-the-toolbox-and-list-tools

"""
import asyncio
from azure.identity import DefaultAzureCredential
import httpx
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession


url = "https://automationhacks-rg-resource.services.ai.azure.com/api/projects/automationhacks-rg/toolboxes/agent-framework-learn-toolbox/mcp?api-version=v1"

token = DefaultAzureCredential().get_token(
    "https://ai.azure.com/.default").token
headers = {
    "Authorization": f"Bearer {token}"
}


async def verify_toolbox():
    async with httpx.AsyncClient(headers=headers) as http_client:
        async with streamable_http_client(url, http_client=http_client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # List available tools
                tools_result = await session.list_tools()
                print(f"Tools found: {len(tools_result.tools)}")

                for tool in tools_result.tools:
                    print(
                        f"    - {tool.name}: {(tool.description or '')[:80]}")

                result = await session.call_tool("", arguments={})
                print(result)


asyncio.run(verify_toolbox())
