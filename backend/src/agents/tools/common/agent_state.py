from langchain.tools import ToolRuntime, tool


@tool
def get_agent_state(runtime: ToolRuntime) -> dict:
    """Return the state of an agent"""
    return runtime.state