import os
from contextlib import contextmanager

from langgraph.checkpoint.postgres import PostgresSaver


@contextmanager
def open_checkpointer():
    db_uri = os.getenv("DB_URI")
    if not db_uri:
        raise ValueError("Environment variable DB_URI not found")
    with PostgresSaver.from_conn_string(db_uri) as checkpointer:
        checkpointer.setup()
        yield checkpointer
