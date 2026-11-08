"""Pool for domain conversations; independent of LangGraph's checkpointer."""
from collections.abc import Generator
from contextlib import contextmanager

from psycopg import Connection
from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from src.infra.db.relational.conversation_repository import ConversationRecord


@contextmanager
def open_conversation_pool(
    db_uri: str,
) -> Generator[ConnectionPool[Connection[ConversationRecord]], None, None]:
    """The application owns this context; repositories only borrow connections."""
    if not db_uri.strip():
        raise ValueError("A PostgreSQL connection URI is required")
    with ConnectionPool[Connection[ConversationRecord]](
        conninfo=db_uri,
        kwargs={"row_factory": class_row(ConversationRecord), "connect_timeout": 5},
        min_size=0,
        max_size=4,
        timeout=5,
        max_idle=60,
        check=ConnectionPool[Connection[ConversationRecord]].check_connection,
        open=True,
    ) as pool:
        yield pool
