from langchain.tools import ToolRuntime, tool


@tool
def test() -> str:
    """Return a message confirming that the testing tool is available."""

    return "I'm using the testing tooling function"


@tool
def common() -> str:
    """Return a message confirming that the common tool is available."""

    return "I'm using the common tooling function"


@tool
def get_agent_state(runtime: ToolRuntime) -> dict:
    """Return the state of a agent"""
    return runtime.state


testing_tools = [test]
common_tools = [common, get_agent_state]
