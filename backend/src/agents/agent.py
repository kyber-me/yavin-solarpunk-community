from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv

from src.global_vars import PROJECT_SRC, PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")

from langchain_core.tools import BaseTool

from langchain.agents import AgentState, create_agent  # pyright: ignore[reportUnknownVariableType]
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph.state import CompiledStateGraph  # pyright: ignore[reportMissingTypeStubs]
from langgraph.types import StateSnapshot
from ulid import ULID

from src.agents.tools.research.web_search import web_search
from src.agents.tools.common.agent_state import get_agent_state
from src.agents.knowledge import retrieval_knowledge

TOOLS: list[BaseTool] = [web_search(), get_agent_state]

# Explore concept
class Attributes:
    pass

# Explore concept
class CustomAgentState(AgentState):
    preferences: dict | None
    attributes: Attributes


class Agent:
    id: str
    name: str
    agent: CompiledStateGraph
    # roles: list[str]  # Create an `Enum` for roles (and permissions)

    # silas = Agent(
    #     agent_record.name, None,
    #     checkpointer,
    #     identity_content=agent_record.identity,
    #     general_documents=general_documents,
    #     agent_id=agent_record.id)
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
        self.agent = create_agent(
            model="gpt-4o-mini",
            tools=TOOLS,
            system_prompt=identity_content,
            checkpointer=checkpointer,
            name=name,
        )

    def invoke(self, message: str, thread_id: str | None) -> dict[str, Any]:
        if not thread_id:
            raise ValueError("thread_id is required")

        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        state = self.agent.get_state(config)
        # Try to understand (why `Sequence`) this need
        messages: Sequence[BaseMessage] = (
            # general_documents: `PROJETO_DE_PESQUISA_YAVIN.md` e `manifesto-solarpunk.md`
            [HumanMessage(message)] if state.values.get("messages") else (
                [SystemMessage(content) for content in self.general_documents] + [HumanMessage(message)]
                if self.general_documents is not None else [SystemMessage(k) for k in retrieval_knowledge()] + [HumanMessage(message)]
            )
        )
        # messages.append(HumanMessage(message))
        result = self.agent.invoke(
            {"messages": messages}, {"configurable": {"thread_id": thread_id}}
        )

        return {"content": result["messages"][-1].content}

    def get_state(
        self, thread_id: str, checkpoint_id: str = "", get_full_history: bool = False
    ) -> list[StateSnapshot]:
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        if checkpoint_id:
            config["configurable"]["checkpoint_id"] = checkpoint_id
        if get_full_history:
            return list(self.agent.get_state_history(config))

        return [self.agent.get_state(config)]




