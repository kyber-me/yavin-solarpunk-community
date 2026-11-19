import os
from contextlib import contextmanager

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore


@contextmanager
def open_checkpointer():
    db_uri = os.getenv("DATABASE_URI")
    if not db_uri:
        raise ValueError("Environment variable DB_URI not found")
    with PostgresSaver.from_conn_string(db_uri) as checkpointer:
        checkpointer.setup()
        yield checkpointer


@contextmanager
def open_store():
    db_uri = os.getenv("DATABASE_URI")
    if not db_uri:
        raise ValueError("Environment variable DB_URI not found")
    with PostgresStore.from_conn_string(db_uri) as store:
        store.setup()
        yield store
