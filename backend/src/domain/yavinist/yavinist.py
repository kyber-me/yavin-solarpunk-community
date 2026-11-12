from typing import Any

from dotenv import load_dotenv
from ulid import ULID
from src.constants import PROJECT_ROOT
load_dotenv(PROJECT_ROOT / ".env")

from langchain_core.tools import BaseTool
from langgraph.checkpoint.postgres import PostgresSaver

from adapters.langchain_container import LangchainAgentContainer, LangchainAgentContainerOptions
from src.agents.tools.research.web_search import web_search
from src.agents.tools.common.agent_state import get_agent_state
from src.adapters.drivens.ollama_provider_adapter import OllamaProviderAdapter
from src.adapters.drivens.qwen3_5_ai_model import Qwen3_5_4bAiModel


TOOLS: list[BaseTool] = [web_search(), get_agent_state]

class Yavinist:
    id: str
    name: str
    agent: LangchainAgentContainer
    # roles: list[str]  # Create an `Enum` for roles (and permissions)


    def __init__(
        self,
        name: str,
        checkpointer: PostgresSaver,
        identity_content: str,
        general_documents: list[str] | None = None,
        agent_id: str | None = None,
    ) -> None:
        self.id = agent_id or str(ULID())
        self.name = name
        self.general_documents = general_documents
        self.agent = LangchainAgentContainer(
            LangchainAgentContainerOptions(
                identity_content=identity_content,
                tools=TOOLS,
                checkpointer=checkpointer,
                name=name
            ),
            OllamaProviderAdapter(
                model_adapter=Qwen3_5_4bAiModel(),
                temperature=0.25
            )
        )


    def send_message(self, message: str, thread_id: str | None) -> dict[str, Any]:
        if not thread_id:
            raise ValueError("thread_id is required")

        return self.agent.invoke(message, thread_id, [])



