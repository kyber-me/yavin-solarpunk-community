from langchain_core.tools import BaseTool

from agents.tools.tools import get_agent_state, web_search
from domain.yavinist import Yavinist
from src.agents.dtos.factory_dto import FactoryDTO

# Built-in cache (implement)
agent_pool = {}

# Roles Vs Capacities -> create an `Enum` for roles (?)
CAPACITIES: dict[str, list[BaseTool]] = {
    "founder": [get_agent_state, web_search()],
    "counselor": [get_agent_state, web_search()],
    "researcher": [get_agent_state, web_search()],
    "engineer": [get_agent_state, web_search()],
    "citizen": [get_agent_state]
}

def build(factory_dto: FactoryDTO) -> Yavinist:
    yavinist_roles = ["counselor"] # Query Database
    name = "Silas" # Query Database
    return Yavinist(
        factory_dto.vector_database,
        factory_dto.checkpointer,
        factory_dto.store,
        yavinist_roles,
        unique_identifier=factory_dto.id,
        name=name,
        identity_prompt=factory_dto.identity_prompt
    )


def _load_tools(roles: list[str]) -> list[BaseTool]:
    tools: list[BaseTool] = []
    for r in roles:
        tools.extend(CAPACITIES[r])

    return tools