# from langgraph.graph.state import CompiledStateGraph
#
# # from src.agents import PROJECT_ROOT, Agent
# from src.constants import PROJECT_ROOT
# from src.domain.yavinist.yavinist import Yavinist
#
#
# def build_agent() -> CompiledStateGraph:
#     from src.agents.infra.open_checkpointer_helper import open_checkpointer
#
#     identity_file = (
#         PROJECT_ROOT / "src" / "agents" / "prompts" / "conversational_behavior" / "SILAS.md"
#     )
#     identity_content = identity_file.read_text(encoding="utf-8")
#     with open_checkpointer() as checkpointer:
#         return Yavinist("Silas", checkpointer, identity_content).agent
