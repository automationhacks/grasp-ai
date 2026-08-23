from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPToolboxTool, ToolSearchToolboxTool, WebSearchToolboxTool


endpoint = "https://automationhacks-rg-resource.services.ai.azure.com/api/projects/automationhacks-rg"
project = AIProjectClient(
    endpoint=endpoint, credential=DefaultAzureCredential())

toolbox_version = project.toolboxes.create_version(
    name="agent-framework-learn-toolbox",
    description="Toolbox with web search and an MCP server",
    tools=[
        WebSearchToolboxTool(),
        MCPToolboxTool(
            server_label="myserver",
            server_url="https://agent-framework-learn.example.com",
            require_approval="never",
            project_connection_id="my-key-auth-connection"
        ),
        ToolSearchToolboxTool(),
    ]
)
print(
    f"Created toolbox: {toolbox_version.name}, version: {toolbox_version.version}")
