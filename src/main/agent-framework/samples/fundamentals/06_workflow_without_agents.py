import asyncio

from agent_framework import workflow

"""
Example shows how to orchestrate async functions with @workflow
Does not require any external services and allows you to call async python functions
in this example to reverse a string and convert it to upper case.
"""


async def to_upper_case(text: str) -> str:
    """
    Convert text into upper case
    """
    return text.upper()


async def reverse_text(text: str) -> str:
    """
    Reverse the string using slice notation in Python
    [start,stop,step], here using :: indicates start at the end and go till the beginning while
    picking one char at a time
    """
    return text[::-1]


@workflow
async def text_workflow(text: str) -> str:
    upper = await to_upper_case(text)
    return await reverse_text(upper)


async def main() -> None:
    workflow_instance = text_workflow.build()
    result = await workflow_instance.run("hello world")
    print(f"Output: {result.get_outputs()}")
    print(f"Final state: {result.get_final_state()}")
    """
    Expected output
    Output: ['DLROW OLLEH']
    Final state: WorkflowRunState.IDLE
    """

if __name__ == '__main__':
    asyncio.run(main())
