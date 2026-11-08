from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
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

BASE_KNOWLEDGE_PATH = PROJECT_ROOT / "src" / "agents" / "base_knowledge"
TOOLS: list[BaseTool] = [web_search(), get_agent_state]

# Explore concept
class Attributes:
    pass

# Explore concept
class CustomAgentState(AgentState):
    preferences: dict | None
    attributes: Attributes


def _retrieval_knowledge() -> list[BaseMessage]:

    # Not every role has access to all documents
    base_knowledge: list[Path] = [
        (BASE_KNOWLEDGE_PATH / "atas"),
        (BASE_KNOWLEDGE_PATH / "manifestos"),
        (BASE_KNOWLEDGE_PATH / "transcriptions"),
    ]

    messages: list[BaseMessage] = []
    try:
        for b in base_knowledge:
            if b.exists():
                if b.is_dir():
                    print(f"Iterate the directory {b.name}")
                    for f in b.iterdir():
                        print(f.suffix.lower())
                        if f.is_file() and f.suffix.lower() == ".md":
                            print(f"Reading the file {f.name}")
                            with open(f, "r") as f_:
                                content = f_.read()
                                messages.append(SystemMessage(content))
                        else:
                            print(
                                f"{f.name} is not a file (needs recursive iteration)"
                            )
                elif b.is_file():
                    with open(b, "r") as f:
                        content = f.read()
                        messages.append(SystemMessage(content))
    except Exception as e:  # noqa: BLE001
        print(e)
        return []

    return messages


class Agent:
    id: str
    name: str
    roles: list[str]  # Create an `Enum` for roles

    agent: CompiledStateGraph

    def __init__(
        self,
        name: str,
        specialized_instructions_path: Path | None,
        checkpointer: PostgresSaver,
    ) -> None:
        self.id = str(ULID())
        self.name = name
        try:
            instructions: str | None = None
            if not specialized_instructions_path:
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
        messages: list[BaseMessage] = (
            [] if state.values.get("messages") else _retrieval_knowledge()
        )

        messages.append(HumanMessage(message))
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




