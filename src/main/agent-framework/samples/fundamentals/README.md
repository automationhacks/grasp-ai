# Agent framework fundamentals

These examples are an almost replica of samples present in microsoft/agent-framework repo under [samples](https://github.com/microsoft/agent-framework/tree/main/python/samples) on GitHub. You can take a look at it there as well. I intend to type these out myself to form a better intuition and leave more human like explainer inline comments that are useful for anyone reading. I try to friendly to beginners, but please pardon me if I assume some pre-requisite knowledge as well.

## Setup

- This project uses `uv` to manage the python dependencies. To setup the env:

```shell
# Install uv for your platform, on mac
# follow https://docs.astral.sh/uv/getting-started/installation/
curl -LsSf https://astral.sh/uv/install.sh | sh
# change to current sample codebase
cd grasp-ai/src/main/agent-framework/samples/fundamentals
# This should create a .venv folder with all required dependencies
uv sync
```

- We are using Microsoft Foundry to get models from. You will need to create an account and setup a project and a model in Foundry. You will need to create a resource group and a model from it. It would then give you couple of information like the endpoint and model to use. Create a `.env` file in `fundamentals` and add below env variables. Most of the standalone files would pick these by using `dotenv`

```shell
FOUNDRY_PROJECT_ENDPOINT="https://<your-resource>.services.ai.azure.com/api/projects/<your-resource-group>"
FOUNDRY_MODEL="<your-model>"
```
