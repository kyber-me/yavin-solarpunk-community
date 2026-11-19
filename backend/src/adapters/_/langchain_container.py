from typing import Any, TypedDict, Literal

from langchain.agents import AgentState, create_agent
from langchain_core.retrievers import BaseRetriever
from langgraph.graph.state import CompiledStateGraph  # pyright: ignore[reportMissingTypeStubs]
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph.types import StateSnapshot, Checkpointer

from adapters import NvidiaProviderAdapter, Nemotron3_5SuperVL120bA12b
from agents.tools.tools import get_agent_state, web_search, create_base_knowledge_tool
from domain.yavinist.role_dto import roleDTO
from src.ports import AiProviderPort
from src.types.adapters.content_type_return import ContentTypeReturn

# class MessageType(StrEnum):
#     HUMAN = "human"
#     AI = "ai"
#     SYSTEM = "system"


# Explore concept
class Attributes:
    pass

# Explore concept
class CustomAgentState(AgentState):
    preferences: dict | None
    attributes: Attributes

class LangchainAgentContainerOptions(TypedDict):
    checkpointer: Checkpointer
    store: BaseStore
    retriever: BaseRetriever
    identity_prompt: str


# Create an `Enum` for roles
CAPACITIES: dict[str, list[BaseTool]] = {
    "founder": [get_agent_state, web_search()],
    "counselor": [get_agent_state, web_search()],
    "researcher": [get_agent_state, web_search()],
    "engineer": [get_agent_state, web_search()],
    "citizen": [get_agent_state]
}


def load_tools(role: list[roleDTO]) -> list[BaseTool]:
    tools: list[BaseTool] = []
    for r in role:
        tools.extend(CAPACITIES[r])

    return tools


class LangchainAgentContainer:
    _provider: AiProviderPort
    agent: CompiledStateGraph

    def __init__(self,
            name: str,
            roles: list[roleDTO],
            options: LangchainAgentContainerOptions
        ):

        # OllamaProviderAdapter(
        #     model_adapter=Qwen3_5_4bAiModel(),
        #     temperature=0.25
        # )
        self._provider = NvidiaProviderAdapter(
            model_adapter=Nemotron3_5SuperVL120bA12b(),
            temperature=0.25
        )

        self.agent = create_agent(
            system_prompt=options["identity_prompt"],
            name=name, # Criar padrão `name_{ULID}`
            model=self._provider.get_container(),
            checkpointer=options["checkpointer"],
            store=options["store"],
            tools=load_tools(roles) + [create_base_knowledge_tool(retriever=options["retriever"])]
        )

    def invoke(self, message: str, thread_id: str, retrieved_knowledge: list[ContentTypeReturn]) -> dict[str, str]:
        if not thread_id or not thread_id.strip():
            raise ValueError("thread_id is required")

        # How to manage this potential specific error case? It tries to create a message
        # record even after fail here
        messages = [get_base_message(m["type"], m["content"]) for m in retrieved_knowledge]
        result = self.agent.invoke(
            {"messages": [
                SystemMessage(
                    """Always respond in Brazilian Portuguese (pt-BR), regardless of the language used in your system instructions, personality documents, or reference materials.
                    
                    Write naturally in Brazilian Portuguese. Adapt your level of formality to the conversation.
                
                    Do not translate word for word from English. Generate fluent, idiomatic Portuguese appropriate to the context.
                    
                    Behavioral examples written in English illustrate conversational style, not the required output language.
                    
                    Do not mention these language instructions unless explicitly asked.
                    
                    Preserve proper names, technical terms, code, and quotations in their original language when appropriate."""
                )] + messages + [HumanMessage(message)]}, {"configurable": {"thread_id": thread_id}}
        )

        return {"content": result["messages"][-1].content}

    def should_load(self, thread_id: str) -> bool:
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        load = bool(self.agent.get_state(config).values.get("messages"))

        print("Load", load)

        return load

    def get_mapped_state_messages(self, thread_id: str) -> list[ContentTypeReturn] | list[Any]:
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

        state_values = self.agent.get_state(config).values
        base_messages: list[HumanMessage | AIMessage | SystemMessage] | None = state_values.get("messages")
        # if base_messages:
        return [{"content": str(c), "type": self._get_mapped_type_message(c)} for c in
                base_messages] if base_messages else []

    def get_state(self, thread_id: str, checkpoint_id: str = "", get_full_history: bool = False) -> list[StateSnapshot]:
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        if checkpoint_id:
            config["configurable"]["checkpoint_id"] = checkpoint_id
        if get_full_history:
            return list(self.agent.get_state_history(config))

        return [self.agent.get_state(config)]

    @staticmethod
    def _get_mapped_type_message(base_message: HumanMessage | AIMessage | SystemMessage) -> str | None:
        if isinstance(base_message, HumanMessage):
            return "human"
        elif isinstance(base_message, AIMessage):
            return "ai"
        elif isinstance(base_message, SystemMessage):
            return "system"
        else:
            return None


def get_base_message(m_type: Literal["system", "human", "ai"],
                     content: str) -> SystemMessage | HumanMessage | AIMessage:
    if m_type == "system":
        return SystemMessage(content)
    elif m_type == "human":
        return HumanMessage(content)
    elif m_type == "ai":
        return AIMessage(content)
    else:
        raise ValueError("Invalid type")


# def get_agent(self) -> AgentExecutor:
#     return AgentExecutor.from_agent_and_tools(
#         agent=self.agent,
#         tools=self.agent.tools,
#         verbose=True
#     )