from typing import Any, cast

from dotenv import load_dotenv
from ulid import ULID
from src.global_vars import PROJECT_ROOT
load_dotenv(PROJECT_ROOT / ".env")

from langchain_core.tools import BaseTool
from langgraph.checkpoint.postgres import PostgresSaver

from src.langchain_agent_container import LangchainAgentContainer, LangchainAgentContainerOptions
from src.langchain_agent_container import ContentTypeReturn
from src.agents.tools.research.web_search import web_search
from src.agents.tools.common.agent_state import get_agent_state
from src.agents.knowledge import retrieval_knowledge
from src.adapters.drivens.OllamaProviderAdapter import OllamaProviderAdapter
from src.adapters.drivens.Qwen3_5AiModel import Qwen3_5_4bAiModel
#from src.adapters.drivens.GptOss20bCloud import GptOss20bCloud


TOOLS: list[BaseTool] = [web_search(), get_agent_state]

class Agent:
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
                #model_adapter=GptOss20bCloud(),
                temperature=0.3
            )
        )


    def invoke(self, message: str, thread_id: str | None) -> dict[str, Any]:
        if not thread_id:
            raise ValueError("thread_id is required")

        load = self.agent.should_load(thread_id)
        # True load guarantees a mapped messages with content
        # mapped_messages = self.agent.get_mapped_state_messages(thread_id)

        messages: list[ContentTypeReturn]
        human_message: ContentTypeReturn = {"content": message, "type": "human"}
        if load: # Load means there is an existent conversation going on and all base knowledge is already loaded
            messages = [human_message]
        else:
            # general_documents: `PROJETO_DE_PESQUISA_YAVIN.md` e `manifesto-solarpunk.md`
            messages: list[ContentTypeReturn] = (
                    [cast(ContentTypeReturn, {"content": content, "type": "system"}) for content in self.general_documents] + [human_message] if self.general_documents
                        else [cast(ContentTypeReturn, {"content": k, "type": "system"}) for k in retrieval_knowledge()] + [human_message]
            )

        return self.agent.invoke(thread_id, messages)

