from langgraph.graph.state import CompiledStateGraph

from src.agents.agent import PROJECT_ROOT, Agent


def build_agent() -> CompiledStateGraph:
    from src.agents.infra.open_checkpointer_helper import open_checkpointer

    identity_file = (
        PROJECT_ROOT / "src" / "agents" / "prompts" / "identities" / "SILAS.md"
    )
    identity_content = identity_file.read_text(encoding="utf-8")
    with open_checkpointer() as checkpointer:
        return Agent("Silas", checkpointer, identity_content).agent
