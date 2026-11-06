# """Obsolete Citizen interface implementation.

# The concrete implementation now lives in ``src.domain.agents.citizen.Citizen``.
# This module is preserved temporarily for historical reference and should not be
# used by new code.
# """

# from pathlib import Path
# from typing import Any, Protocol

# from langchain.agents import AgentState, create_agent
# from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
# from langchain_core.runnables import RunnableConfig
# from langgraph.checkpoint.memory import InMemorySaver
# from langgraph.graph.state import CompiledStateGraph
# from langgraph.types import StateSnapshot

# from agents.main import common_tools as common
# from agents.main import testing_tools as testing

# PROJECT_ROOT = Path(__name__).resolve().parents[0]
# BASE_KNOWLEDGE_PATH = PROJECT_ROOT.joinpath("docs")
# TOOLS = [*common, *testing]

# from dotenv import load_dotenv

# load_dotenv()


# # Explore concept
# class Attributes:
#     pass


# # Explore concept
# class CustomAgentState(AgentState):
#     citizen_id: str
#     preferences: dict | None
#     attributes: Attributes


# class Citizen(Protocol):
#     BASE_KNOWLEDGE: list[Path] | None

#     agent: CompiledStateGraph
#     name: str

#     def __init__(self, citizen_name: str, id_instructions_path: Path | None) -> None:
#         super().__init__()

#         self.BASE_KNOWLEDGE: list[Path] | None = [
#             (BASE_KNOWLEDGE_PATH / "atas"),
#             (BASE_KNOWLEDGE_PATH / "manifestos"),
#             (BASE_KNOWLEDGE_PATH / "transcriptions"),
#         ]
#         self.name = citizen_name

#         try:
#             instructions: str | None = None
#             if not id_instructions_path:
#                 pass
#             else:
#                 with open(id_instructions_path, "r") as f:
#                     instructions = f.read()

#         except Exception as e:  # noqa: BLE001
#             print(e)
#             raise Exception  # noqa: TRY002

#         self.agent = create_agent(
#             model="gpt-4o-mini",
#             tools=TOOLS,
#             system_prompt=instructions,
#             checkpointer=InMemorySaver(),
#             name=citizen_name,
#         )

#     def invoke(self, human_message: str, thread_id: str | None) -> Any:

#         messages: list[BaseMessage] = self._retrieval_knowledge()

#         messages.append(HumanMessage(human_message))
#         result = self.agent.invoke(
#             {"messages": messages}, {"configurable": {"thread_id": thread_id}}
#         )
#         # print(f"Result\n: {result}\n")
#         print(type(result), "\n")
#         print(result["messages"][-1].content_blocks)

#         return result

#     def _retrieval_knowledge(self) -> list[BaseMessage]:

#         messages: list[BaseMessage] = []
#         try:
#             if self.BASE_KNOWLEDGE and len(self.BASE_KNOWLEDGE):
#                 for b in self.BASE_KNOWLEDGE:
#                     if b.exists():
#                         if b.is_dir():
#                             print(f"Iterate the directory {b.name}")
#                             for f in b.iterdir():
#                                 print(f.suffix.lower())
#                                 if f.is_file() and f.suffix.lower() == ".md":
#                                     print(f"Reading the file {f.name}")
#                                     with open(f, "r") as f:
#                                         content = f.read()
#                                         messages.append(SystemMessage(content))
#                                 else:
#                                     print(
#                                         f"{f.name} is not a file (needs recursive iteration)"
#                                     )
#                         elif b.is_file():
#                             with open(b, "r") as f:
#                                 content = f.read()
#                                 messages.append(SystemMessage(content))
#         except Exception as e:  # noqa: BLE001
#             print(e)
#             return []

#         return messages

#     def get_name(self) -> str:
#         return self.name

#     def get_state(
#         self, thread_id: str, checkpoint_id: str = "", get_full_history: bool = False
#     ) -> list[StateSnapshot]:
#         config: RunnableConfig = {
#             "configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}
#         }
#         if get_full_history:
#             return list(self.agent.get_state_history(config))

#         return [self.agent.get_state(config)]
