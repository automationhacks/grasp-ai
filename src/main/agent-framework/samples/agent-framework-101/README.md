# Agent framework 101

This project follows examples from [Quickstart: Get started with Microsoft Foundry SDK](https://learn.microsoft.com/en-us/azure/foundry/quickstarts/get-started-code?tabs=python) to understand how Microsoft Agent framework works with Foundry.

Microsoft Foundry can be thought of as an SDK/API layer that provides your apps easy access to models from different providers. These models would be running on Azure Infra. By getting access to these models, you can then build agents or AI apps or integrate AI models in your existing apps.

After finishing this, you can also go through this [Tutorial: Idea to prototype - Build and evaluate an enterprise agent](https://learn.microsoft.com/en-us/azure/foundry/tutorials/developer-journey-idea-to-prototype?tabs=python) for a more practical tutorial on building Agents with foundry.

After this basic introduction, you can start to go through [Meet your agent harness and claw](https://devblogs.microsoft.com/agent-framework/meet-your-agent-harness-and-claw/) to understand how Microsoft Agent framework could be helpful to wrap a chat model with surrounding harness.

## Meet your agent harness and claw

In this we build a custom agent by wrapping agent framework (or harness) around a chat client. Using Agent framework gives features like memory, planning, history, tool calling, web search out of the box and a developer does not have to worry about this.

## Setup

- Under your user root folder `/Users/<your-user-name>`, clone [Microsoft/agentframework](https://github.com/microsoft/agent-framework) repo as we reuse the terminal UI library from there for this local agent demo. You can run below

```shell
gh repo clone microsoft/agent-framework
```

- After setup, you can run `uv run <file>` under `src/main/agent-framework/samples/agent-framework-101` to spin up the desired example agent. The examples from 04 onwards follow the building your own claw blog series and would be in sync with [build_your_own_claw](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/harness/build_your_own_claw) series
