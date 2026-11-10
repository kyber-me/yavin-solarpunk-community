from typing import Any, Sequence, TypedDict, Literal #Annotated,

from langchain.agents import AgentState, create_agent
from langgraph.graph.state import CompiledStateGraph  # pyright: ignore[reportMissingTypeStubs]
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import StateSnapshot

from src.ports.drivens.ai_provider_port import AiProviderPort
from src.types.adapters.content_type_return import ContentTypeReturn

# Explore concept
class Attributes:
    pass

# Explore concept
class CustomAgentState(AgentState):
    preferences: dict | None
    attributes: Attributes

class LangchainAgentContainerOptions(TypedDict):
    identity_content: str
    tools: Sequence[BaseTool]
    checkpointer: PostgresSaver
    name: str

# class MessageType(StrEnum):
#     HUMAN = "human"
#     AI = "ai"
#     SYSTEM = "system"


class LangchainAgentContainer:
    _provider: AiProviderPort
    agent: CompiledStateGraph

    def __init__(self, options: LangchainAgentContainerOptions, ai_provider: AiProviderPort):
        # super().__init__()
        self._provider = ai_provider
        self.agent = create_agent(
            model=ai_provider.get_container(),
            system_prompt=options["identity_content"],
            checkpointer=options["checkpointer"],
            tools=options["tools"],
            name=options["name"],
        )


    def invoke(self, thread_id: str, retrieval_knowledge_base: list[ContentTypeReturn]) -> dict[str, str]:
        if not thread_id or not thread_id.strip():
            raise ValueError("thread_id is required")

        def get_base_message(m_type: Literal["system", "human", "ai"], content: str) -> SystemMessage | HumanMessage | AIMessage:
            if m_type == "system":
                return SystemMessage(content)
            elif m_type == "human":
                return HumanMessage(content)
            elif m_type == "ai":
                return AIMessage(content)
            else:
                raise ValueError("Invalid type")

        # How to manage this potential specific error case? It tries to create a message
        # record even after fail here
        messages = [get_base_message(m["type"], m["content"]) for m in retrieval_knowledge_base]
        result = self.agent.invoke(
            {"messages": messages}, {"configurable": {"thread_id": thread_id}}
        )

        print("Result: ", result)
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
        return [{"content": str(c), "type": self._get_mapped_type_message(c)} for c in base_messages] if base_messages else []


    def get_state(self, thread_id: str, checkpoint_id: str = "", get_full_history: bool = False
    ) -> list[StateSnapshot]:
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



# def get_agent(self) -> AgentExecutor:
#     return AgentExecutor.from_agent_and_tools(
#         agent=self.agent,
#         tools=self.agent.tools,
#         verbose=True
#     )
