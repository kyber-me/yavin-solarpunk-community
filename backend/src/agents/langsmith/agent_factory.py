from langgraph.graph.state import CompiledStateGraph

from src.agents.agent import PROJECT_ROOT, Agent


def build_agent() -> CompiledStateGraph:
    from src.agents.infra.open_checkpointer_helper import open_checkpointer

    identity_path = (
        PROJECT_ROOT / "src" / "agents" / "prompts" / "IDENTIDADE_ID_SILAS.md"
    )
    with open_checkpointer() as checkpointer:
        return Agent("Silas", identity_path, checkpointer).agent
