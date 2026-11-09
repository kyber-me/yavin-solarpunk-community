from typing import TypedDict
from src.persistence.db.relational.agent_repository import AgentRecord


# {
    # "manifesto": "412778d5150b81438b72e2ade85b77b5",
    # "research_project": "412778d5150b81c3a2aee23bfb35a766"
# }
class CacheContainer(TypedDict):
    # general_documents: dict[Literal["manifesto", "research_project"], str | None] | None
    general_documents: list[str] | None
    agents: dict[str, AgentRecord | None]

cache_container: CacheContainer = {"agents": {}, "general_documents": None}
