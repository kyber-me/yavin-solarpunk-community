from ulid import ULID

from src.agents.agent import PROJECT_ROOT, Agent
from src.agents.infra.open_checkpointer_helper import open_checkpointer

identity_path = (
    PROJECT_ROOT / "src" / "agents" / "prompts" / "IDENTIDADE_ID_SILAS.md"
)
with open_checkpointer() as checkpointer:
    a = Agent("Silas", identity_path, checkpointer)
    result = a.invoke("Me fale um pouco de você", str(ULID()))

    # result["messages"][-1].content_blocks
    for k, v in result.items():
        print(f"{k} -> {v[:100]}", end="\n\n")
