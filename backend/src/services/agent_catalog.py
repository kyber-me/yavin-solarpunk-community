"""Minimal backend-owned catalog shared by discovery and conversation creation."""
from src.types.dtos.agent_catalog import AgentCatalog, AgentSummary


_AVAILABLE_AGENTS: tuple[tuple[str, str], ...] = (("silas", "Silas"),)


def get_agent_catalog() -> AgentCatalog:
    return AgentCatalog(agents=[AgentSummary(id=agent_id, name=name) for agent_id, name in _AVAILABLE_AGENTS])


def is_agent_available(participant_id: str) -> bool:
    return any(agent_id == participant_id for agent_id, _ in _AVAILABLE_AGENTS)
