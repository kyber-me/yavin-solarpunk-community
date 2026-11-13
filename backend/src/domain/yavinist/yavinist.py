from typing import Any

from dotenv import load_dotenv
from ulid import ULID

from src.domain.yavinist import roleDto
from src.constants import PROJECT_ROOT
load_dotenv(PROJECT_ROOT / ".env")

from langchain_core.tools import BaseTool
from langgraph.checkpoint.postgres import PostgresSaver

from src.agents.tools.tools import web_search, get_agent_state
from src.adapters import (
    LangchainAgentContainer,
    LangchainAgentContainerOptions,
    NvidiaProviderAdapter,
    Nemotron3_5SuperVL120bA12b,
    # OllamaProviderAdapter,
    # Qwen3_5_4bAiModel
)



# Roles Vs Capacities -> create an `Enum` for roles (?)
CAPACITIES: dict[str, list[BaseTool]] = {
    "founder": [get_agent_state, web_search()],
    "counselor": [get_agent_state, web_search()],
    "researcher": [get_agent_state, web_search()],
    "engineer": [get_agent_state, web_search()],
    "citizen": [get_agent_state]
}

class Yavinist:
    id: str
    name: str
    role: list[roleDto.role]

    agent: LangchainAgentContainer

    def __init__(
        self,
        checkpointer: PostgresSaver,
        role: list[roleDto.role],
        *,
        name: str,
        identity_content: str, # Is that really necessary?
        agent_id: str | None = None, # Investigate it
    ) -> None:
        self.id = agent_id or str(ULID())
        self.name = name
        self.role = role
        self.agent = LangchainAgentContainer(
            LangchainAgentContainerOptions(
                identity_content=identity_content,
                tools=self.load_tools(),
                checkpointer=checkpointer,
                name=name
            ),
            NvidiaProviderAdapter(
                model_adapter=Nemotron3_5SuperVL120bA12b(),
                temperature=0.25
            )
            # OllamaProviderAdapter(
            #     model_adapter=Qwen3_5_4bAiModel(),
            #     temperature=0.25
            #)
        )


    def send_message(self, message: str, thread_id: str | None) -> dict[str, Any]:
        if not thread_id:
            raise ValueError("thread_id is required")

        return self.agent.invoke(message, thread_id, [])

    def load_tools(self) -> list[BaseTool]:
        tools: list[BaseTool] = []
        for r in self.role:
            tools.extend(CAPACITIES[r])

        return tools




