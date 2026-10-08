

import asyncio

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, executor, handler
from typing_extensions import Never

"""
How a graph workflow can be created

Executable code can be written in a class inheriting from Executor and methods annotated with @handler
These methods are passed WorkflowContext which allows passing of state across different executors in the graph

Similarly methods can also be annotated with @executor and can perform similar send_message, yield_output operations

Workflow graph can be combined by using WorkflowBuilder with add_edge to connect nodes and eventually be run()

The graph API supports:
1. Creating edges
2. fan out/fan in
3. switch/case
4. superstep based checkpointing (this is interesting, it uses BSP (Bulk synchronous processing) which is used for distributed graph processing)
"""

# Class based Executor that converts text into upper case


class UpperCase(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def to_upper_case(self, text: str, ctx: WorkflowContext[str]) -> None:
        """Convert input to upper case and forward it to the next node"""
        await ctx.send_message(text.upper())


@executor(id="reverse_text")
async def reverse_text(text: str, ctx: WorkflowContext[Never, str]):
    """
    Reverse the string and yield the final workflow output
    """
    await ctx.yield_output(text[::-1])


def create_workflow():
    upper = UpperCase(id="upper_case")
    return WorkflowBuilder(start_executor=upper).add_edge(upper, reverse_text).build()


async def main() -> None:
    workflow = create_workflow()

    events = await workflow.run("hello world")
    print(f"Output: {events.get_outputs()}")
    print(f"Final state: {events.get_final_state()}")
    """
    Expected output:
        Output: ['DLROW OLLEH']
        Final state: WorkflowRunState.IDLE
    """


if __name__ == '__main__':
    asyncio.run(main())
