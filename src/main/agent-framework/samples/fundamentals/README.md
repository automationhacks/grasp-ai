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

- We are using Microsoft Foundry to get models from. You will need to create an account and setup a project and a model in Foundry. You will need to create a resource group and a model from it. It would then give you couple of information like the endpoint and model to use. Create a `.env` file in `fundamentals` and add below env variables. Most of the standalone files would pick these by using `dotenv`. If you are new to Foundry, I'll recommend following [Quickstart: Set up Microsoft Foundry resources](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources?tabs=azurecli) to create required resources, project and deploy a model. You can either use CLI or the portal itself to help with creation of resources. Choose the tool that you are most comfortable with to start with.

With CLI, you can follow below steps:

```shell
# Check if azure cli is installed
az version

# Login to azure cli
az login

# Create a resource group
az group create --name automation-hacks-rg --location eastus

# Create a foundry resource
az cognitiveservices account create --name automation-hacks-resource --resource-group automation-hacks-rg --kind AIServices --sku S0 --location eastus --custom-domain automation-hacks-resource --allow-project-management

# Create a project
az cognitiveservices account project create --name my-foundry-resource --resource-group my-foundry-rg --project-name my-foundry-project --location eastus

# Check resource is provisioned
az cognitiveservices account show --name automationhacks-rg-resource --resource-group automationhacks-rg --query properties.provisioningState --output tsv
```

```shell
FOUNDRY_PROJECT_ENDPOINT="https://<your-resource>.services.ai.azure.com/api/projects/<your-resource-group>"
FOUNDRY_MODEL="<your-model>"
```
