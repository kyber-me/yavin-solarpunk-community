"""Explicit PostgreSQL operations, without HTTP or agent dependencies."""
import json
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from psycopg import Connection
from psycopg.errors import UniqueViolation

if TYPE_CHECKING:
    from psycopg_pool import ConnectionPool


ACTIVE_LOOKUP_INDEX = "conversations_active_lookup_uq"
COLUMNS = "id, sender_id, participant_id, look_up_key, thread_id, created_at, start_date, end_date, active"


def conversation_lookup(sender_id: str, participant_id: str) -> str:
    """An unordered pair, encoded without separator collisions or ID rewriting."""
    if not sender_id.strip() or not participant_id.strip():
        raise ValueError("Both participant IDs are required")
    if sender_id == participant_id:
        raise ValueError("A conversation requires distinct participants")
    return json.dumps(sorted([sender_id, participant_id]), ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True)
class ConversationRecord:
    id: str
    sender_id: str
    participant_id: str
    look_up_key: str
    thread_id: str
    created_at: datetime
    start_date: datetime | None = None
    end_date: datetime | None = None
    active: bool = True


class ActiveConversationExists(Exception):
    def __init__(self, conversation: ConversationRecord) -> None:
        super().__init__("An active conversation already exists for these participants")
        self.conversation = conversation


class PostgresConversationRepository:
    def __init__(self, pool: "ConnectionPool[Connection[ConversationRecord]]") -> None:
        self._pool = pool

    def get_by_id(self, conversation_id: str) -> ConversationRecord | None:
        with self._pool.connection() as connection:
            return connection.execute(
                f"SELECT {COLUMNS} FROM yavin.conversations WHERE id = %s",
                (conversation_id,),
            ).fetchone()

    def get_active_by_lookup(self, look_up_key: str) -> ConversationRecord | None:
        with self._pool.connection() as connection:
            return connection.execute(
                f"SELECT {COLUMNS} FROM yavin.conversations WHERE look_up_key = %s AND active",
                (look_up_key,),
            ).fetchone()

    def create(self, conversation: ConversationRecord) -> ConversationRecord:
        expected_lookup = conversation_lookup(conversation.sender_id, conversation.participant_id)
        if conversation.look_up_key != expected_lookup:
            raise ValueError("look_up_key must be the canonical unordered participant pair")
        for timestamp in (conversation.created_at, conversation.start_date, conversation.end_date):
            if timestamp is not None and timestamp.utcoffset() is None:
                raise ValueError("Conversation timestamps must include a timezone")
        existing = self.get_active_by_lookup(conversation.look_up_key) if conversation.active else None
        if existing is not None:
            raise ActiveConversationExists(existing)
        try:
            with self._pool.connection() as connection:
                saved = connection.execute(
                    f"INSERT INTO yavin.conversations ({COLUMNS}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING {COLUMNS}",
                    (
                        conversation.id, conversation.sender_id, conversation.participant_id,
                        conversation.look_up_key, conversation.thread_id, conversation.created_at,
                        conversation.start_date, conversation.end_date, conversation.active,
                    ),
                ).fetchone()
                if saved is None:
                    raise RuntimeError("The conversation insert returned no record")
                return saved
        except UniqueViolation as error:
            # The connection context has rolled back before we attempt another query.
            if error.diag.constraint_name == ACTIVE_LOOKUP_INDEX:
                existing = self.get_active_by_lookup(conversation.look_up_key)
                if existing is not None:
                    raise ActiveConversationExists(existing) from error
            raise
