# Weather

This is an example MCP server that can be connected to an MCP client in order to allow LLM's to make use of the provided tools in order to provide a function

Taken from Model context protocol wiki on [Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server)

## Setup

If you use Claude desktop, then add below to `code ~/Library/Application\ Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT/FOLDER/weather",
        "run",
        "weather.py"
      ]
    }
  }
}
```

If you are using VSCode

```json
{
  "servers": {
    "weather-mcp": {
      "type": "stdio",
      "command": "/Users/gauravsingh/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/Users/gauravsingh/self/grasp-ai/src/main/mcp/servers/weather/weather.py"
      ]
    }
  },
  "inputs": []
}
```

## MCP inspector

```bash
npx @modelcontextprotocol/inspector \
  /Users/gauravsingh/.local/bin/uv \
  run /Users/gauravsingh/self/grasp-ai/src/main/mcp/servers/weather/weather.py
```

## Workflow

Once configured

1. Client sends a request to LLM
2. LLM analyzes available tools and chooses which one to use
3. Client executes tool via MCP server
4. Results are sent back to LLM
5. LLM parses results and forms a response in english
6. LLM sends the response back to client
