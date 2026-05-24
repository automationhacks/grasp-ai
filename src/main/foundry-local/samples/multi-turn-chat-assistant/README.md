# Multi turn chat assistant

This tutorial follows [Tutorial: Build a multi-turn chat assistant with Foundry Local](https://learn.microsoft.com/en-us/azure/foundry-local/tutorials/tutorial-build-chat-assistant?tabs=xplatform&pivots=programming-language-python)

## Setup

We are using `uv` for package management, follow [installation](https://docs.astral.sh/uv/getting-started/installation/) steps for your platform

```shell
curl -LsSf https://astral.sh/uv/0.11.16/install.sh | sh
```

And then run

```shell
# Install required packages and setup virtualenv
uv sync
# Check packages are installed in pip
uv pip list
```

## Running the agent

Run below command to run the AI agent and then chat naturally:

```shell
uv run main.py
```
