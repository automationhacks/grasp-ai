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

### Memory

Microsoft Agent framework harness provides support for memory, there are 2 types:

1. File memory: This is coarse, full file memory saved locally by the agent to capture notes, todos, watchlist etc.
2. Foundry memory: These are small facts that are derived from the different chat sessions and stored in a memory store in foundry. These are extracted automatically from agent conversations as durable facts that can be reused later on. For e.g. this customer prefers low risk ETFs;and is saving money to buy his own house.

### Skills

- There are 2 types of skills:
  - **File based skills**: Skill files in your repo
  - **Foundry based skills**: Skill files which lie in foundry and can be managed and edited there without making a repo change or re-deploying.
- You can create skills which can share know how on how to tackle different scenarios for your agents within agent framework, read [Give Your Agents Domain Expertise with Agent Skills in Microsoft Agent Framework by Serhiy Menshykh](https://devblogs.microsoft.com/agent-framework/give-your-agents-domain-expertise-with-agent-skills-in-microsoft-agent-framework/) to understand more.

```python
from agent_framework import SkillsProvider

skills_provider = SkillsProvider.from_paths(
            skill_paths=[str(_SKILLS_DIR)],
            # below let's the skills scripts run
            script_runner=subprocess_script_runner.subprocess_script_runner
        )

agent = create_harness_agent(
            client=client,
            agent_instructions=FINANCE_INSTRUCTIONS,
            tools=[get_stock_price, place_trade],
            file_access_store=FileSystemAgentFileStore(str(_WORKING_DIR)),
            auto_approval_rules=[
                FileAccessProvider.read_only_tools_auto_approval_rule,
                auto_approve_small_trades,
            ],
            context_providers=context_providers or None,
            mode_provider=AgentModeProvider(default_mode="execute"),
            # add the skills provider to creation of agent harness
            skills_provider=skills_provider
        )
```

You can also add skills in Foundry and then reuse them in your agent. When skills change, this would help prevent redeployment.
