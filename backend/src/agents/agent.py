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

    def __init__(
        self,
        name: str,
        specialized_instructions_path: Path | None,
        checkpointer: PostgresSaver,
        identity_content: str | None = None,
        general_documents: list[str] | None = None,
        agent_id: str | None = None,
    ) -> None:
        self.id = agent_id or str(ULID())
        self.name = name
        self.general_documents = general_documents

        # It is really necessary to catch an Exception here?
        try:
            instructions: str | None = None
            if identity_content is not None:
                instructions = identity_content
            elif not specialized_instructions_path:
                pass
            else:
                with open(specialized_instructions_path, "r") as f:
                    instructions = f.read()

        except Exception as e:  # noqa: BLE001
            print(e)
            raise Exception  # noqa: TRY002

        self.agent = create_agent(
            model="gpt-4o-mini",
            tools=TOOLS,
            system_prompt=instructions,
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
            [HumanMessage(message)] if state.values.get("messages") else (
                [SystemMessage(content) for content in self.general_documents] +
                [SystemMessage(k) for k in retrieval_knowledge(include_manifesto=False)] + [HumanMessage(message)]
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




