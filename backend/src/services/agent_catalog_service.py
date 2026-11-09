"""Minimal backend-owned catalog shared by discovery and conversation creation."""
from src.types.dtos.agent_catalog import AgentCatalog, AgentSummary
from src.persistence.db.relational.agent_repository import AgentRepository


def get_agent_catalog(pool) -> AgentCatalog:
    return AgentCatalog(agents=[AgentSummary(id=agent_id, name=name, public_description=description) for agent_id, name, description in AgentRepository(pool).list_agents()])


def is_agent_available(participant_id: str, pool) -> bool:
    return AgentRepository(pool).get(participant_id) is not None
