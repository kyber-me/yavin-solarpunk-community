"""Explicit PostgreSQL operations, without HTTP or agent dependencies."""
from typing import TYPE_CHECKING

from psycopg import Connection
from psycopg.errors import UniqueViolation

from src.persistence.db.relational.conversation_record import ConversationRecord

if TYPE_CHECKING:
    from psycopg_pool import ConnectionPool


ACTIVE_PAIR_INDEX = "conversations_active_pair_uq"
COLUMNS = "id, sender_id, participant_id, thread_id, created_at, start_date, end_date, active, title"


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

    def list_by_participant(self, participant_id: str, *, limit: int = 100, offset: int = 0) -> list[ConversationRecord]:
        if not 1 <= limit <= 1000 or offset < 0:
            raise ValueError("Invalid pagination")
        with self._pool.connection() as connection:
            return connection.execute(
                f"SELECT {COLUMNS} FROM yavin.conversations WHERE sender_id = %s OR participant_id = %s "
                "ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
                (participant_id, participant_id, limit, offset),
            ).fetchall()

    def get_active_by_participants(self, sender_id: str, participant_id: str) -> ConversationRecord | None:
        with self._pool.connection() as connection:
            return connection.execute(
                f"SELECT {COLUMNS} FROM yavin.conversations "
                "WHERE LEAST(sender_id, participant_id) = LEAST(%s::text, %s::text) "
                "AND GREATEST(sender_id, participant_id) = GREATEST(%s::text, %s::text) AND active",
                (sender_id, participant_id, sender_id, participant_id),
            ).fetchone()

    def create(self, conversation: ConversationRecord) -> ConversationRecord:
        if not conversation.sender_id.strip() or not conversation.participant_id.strip():
            raise ValueError("Both participant IDs are required")
        if not conversation.title.strip() or len(conversation.title) > 120:
            raise ValueError("A valid conversation title is required")
        if conversation.sender_id == conversation.participant_id:
            raise ValueError("A conversation requires distinct participants")
        for timestamp in (conversation.created_at, conversation.start_date, conversation.end_date):
            if timestamp is not None and timestamp.utcoffset() is None:
                raise ValueError("Conversation timestamps must include a timezone")
        existing = self.get_active_by_participants(conversation.sender_id, conversation.participant_id) if conversation.active else None
        if existing is not None:
            raise ActiveConversationExists(existing)
        try:
            with self._pool.connection() as connection:
                saved = connection.execute(
                    f"INSERT INTO yavin.conversations ({COLUMNS}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING {COLUMNS}",
                    (
                        conversation.id, conversation.sender_id, conversation.participant_id,
                        conversation.thread_id, conversation.created_at,
                        conversation.start_date, conversation.end_date, conversation.active, conversation.title,
                    ),
                ).fetchone()
                if saved is None:
                    raise RuntimeError("The conversation insert returned no record")
                return saved
        except UniqueViolation as error:
            # The connection context has rolled back before we attempt another query.
            if error.diag.constraint_name == ACTIVE_PAIR_INDEX:
                existing = self.get_active_by_participants(conversation.sender_id, conversation.participant_id)
                if existing is not None:
                    raise ActiveConversationExists(existing) from error
            raise

    def update_title(self, conversation_id: str, owner_id: str, title: str) -> ConversationRecord | None:
        with self._pool.connection() as connection:
            return connection.execute(
                f"UPDATE yavin.conversations SET title = %s WHERE id = %s AND sender_id = %s RETURNING {COLUMNS}",
                (title, conversation_id, owner_id),
            ).fetchone()
