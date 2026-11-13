"""Agent and mandatory document records. General documents have no agent FK."""
from dataclasses import dataclass
from pathlib import Path

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from ulid import ULID


MANIFESTO_PAGE = "412778d5150b81438b72e2ade85b77b5"
PROJECT_PAGE = "412778d5150b81c3a2aee23bfb35a766"
IDENTITY_FILE = Path(__file__).resolve().parents[3] / "agents/prompts/conversational_behavior/silas/SILAS_v5.md"


@dataclass(frozen=True)
class AgentRecord:
    id: str
    name: str
    identity: str


class AgentRepository:
    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    def seed(self) -> None:
        identity = IDENTITY_FILE.read_text(encoding="utf-8")
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute("INSERT INTO agents (id, name) VALUES (%s, 'Silas') ON CONFLICT (name) DO NOTHING", (str(ULID()),))
                cursor.execute("SELECT id FROM agents WHERE name = 'Silas'")
                agent_id = cursor.fetchone()["id"]
                cursor.execute(
                    "INSERT INTO documents (id, kind, agent_id, content) VALUES (%s, 'identity', %s, %s)"
                    " ON CONFLICT (agent_id) WHERE kind = 'identity' DO UPDATE SET content = EXCLUDED.content",
                    # " ON CONFLICT ON CONSTRAINT documents_identity_agent_uq DO UPDATE SET content = EXCLUDED.content",
                    (str(ULID()), agent_id, identity)
                )
                for kind, page in (("manifesto", MANIFESTO_PAGE), ("research_project", PROJECT_PAGE)):
                    cursor.execute("INSERT INTO documents (id, kind, notion_page_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (str(ULID()), kind, page))

    def list_agents(self) -> list[tuple[str, str, str | None]]:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute("SELECT a.id, a.name, a.public_description FROM agents a WHERE EXISTS (SELECT 1 FROM documents d WHERE d.agent_id = a.id AND d.kind = 'identity') ORDER BY a.name")
                return [(row["id"], row["name"], row["public_description"]) for row in cursor.fetchall()]

    def get(self, agent_id: str) -> AgentRecord | None:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute("SELECT a.id, a.name, d.content AS identity FROM agents a JOIN documents d ON d.agent_id = a.id AND d.kind = 'identity' WHERE a.id = %s", (agent_id,))
                row = cursor.fetchone()
                return AgentRecord(**row) if row else None

    def general_pages(self) -> dict[str, str]:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute("SELECT kind, notion_page_id FROM documents WHERE agent_id IS NULL")
                return {row["kind"]: row["notion_page_id"] for row in cursor.fetchall()}
