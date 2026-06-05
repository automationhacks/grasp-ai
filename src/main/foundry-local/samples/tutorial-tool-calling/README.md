# AI Assistant with tool calling

- You can define tools as functions with their schema in a JSON file
- With tool calling, model can request to run a function
- It does not run functions directly, it returns a tool call request with function name and arguments
- Your code runs the function
- and model then returns the result

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

This project uses below dependencies

```toml
dependencies = [
    "foundry-local-sdk>=1.1.0",
    "openai>=2.36.0",
]
```
