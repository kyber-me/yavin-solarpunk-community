"""Synchronous message persistence; callers supply the existing application pool."""
from typing import TYPE_CHECKING

from psycopg import Connection
from psycopg.rows import class_row

from src.infra.db.relational.conversation_record import ConversationRecord
from src.infra.db.relational.message_record import MessageRecord

if TYPE_CHECKING:
    from psycopg_pool import ConnectionPool


COLUMNS = "id, conversation_id, sender_id, content, created_at, updated_at, deleted_at"


class PostgresMessageRepository:
    def __init__(self, pool: "ConnectionPool[Connection[ConversationRecord]]") -> None:
        self._pool = pool

    def create(self, message: MessageRecord) -> MessageRecord:
        for value in (message.id, message.conversation_id, message.sender_id, message.content):
            if not value.strip():
                raise ValueError("Message IDs, sender and content must not be blank")
        for timestamp in (message.created_at, message.updated_at, message.deleted_at):
            if timestamp is not None and timestamp.utcoffset() is None:
                raise ValueError("Message timestamps must include a timezone")
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=class_row(MessageRecord)) as cursor:
                saved = cursor.execute(
                    f"INSERT INTO yavin.messages ({COLUMNS}) "
                    f"VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING {COLUMNS}",
                    (message.id, message.conversation_id, message.sender_id, message.content,
                     message.created_at, message.updated_at, message.deleted_at),
                ).fetchone()
                if saved is None:
                    raise RuntimeError("The message insert returned no record")
                return saved

    def get_by_id(self, message_id: str) -> MessageRecord | None:
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=class_row(MessageRecord)) as cursor:
                return cursor.execute(
                    f"SELECT {COLUMNS} FROM yavin.messages WHERE id = %s", (message_id,)
                ).fetchone()

    def list_by_conversation(self, conversation_id: str, *, limit: int = 100, offset: int = 0) -> list[MessageRecord]:
        """Return the earliest messages, including deletion metadata, in stable order."""
        if not 1 <= limit <= 1000 or offset < 0:
            raise ValueError("Invalid pagination")
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=class_row(MessageRecord)) as cursor:
                return cursor.execute(
                    f"SELECT {COLUMNS} FROM yavin.messages WHERE conversation_id = %s "
                    "ORDER BY created_at, id LIMIT %s OFFSET %s", (conversation_id, limit, offset),
                ).fetchall()
