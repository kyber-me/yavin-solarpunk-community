from pathlib import Path
from typing import Any

from langchain.agents import AgentState, create_agent
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot
from ulid import ULID

from src.agents.tools import common_tools as common
from src.agents.tools import testing_tools as testing

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE_KNOWLEDGE_PATH = PROJECT_ROOT / "src" / "agents" / "base_knowledge"
TOOLS = [*common, *testing]

from dotenv import load_dotenv

load_dotenv()


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
    roles: list[str]  # Create a Enum for roles

    agent: CompiledStateGraph

    def __init__(self, name: str, specialized_instructions_path: Path | None) -> None:
        super().__init__()  # Do why should `super()` be called?

        self.id = f"Agen_{ULID()}"
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
            checkpointer=InMemorySaver(),
            name=name,
        )

    def invoke(self, human_message: str, thread_id: str | None) -> dict[str, Any]:

        messages: list[BaseMessage] = self._retrieval_knowledge()

        messages.append(HumanMessage(human_message))
        result = self.agent.invoke(
            {"messages": messages}, {"configurable": {"thread_id": thread_id}}
        )

        return {"content": result["messages"][-1].content}

    def _retrieval_knowledge(self) -> list[BaseMessage]:

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
                                with open(f, "r") as f:
                                    content = f.read()
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

    def get_name(self) -> str:
        return self.name

    def get_state(
        self, thread_id: str, checkpoint_id: str = "", get_full_history: bool = False
    ) -> list[StateSnapshot]:
        config: RunnableConfig = {
            "configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}
        }
        if get_full_history:
            return list(self.agent.get_state_history(config))

        return [self.agent.get_state(config)]


if __name__ == "__main__":
    print("Executing as a script...")

    identity_path = (
        PROJECT_ROOT / "src" / "agents" / "prompts" / "IDENTIDADE_ID_SILAS.md"
    )
    a = Agent("Silas", identity_path)
    result = a.invoke("Me fale um pouco de você", "test-1")

    # result["messages"][-1].content_blocks
    for k, v in result.items():
        print(f"{k} -> {v[:100]}", end="\n\n")
