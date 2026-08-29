from contextlib import contextmanager
from typing import Any

from config import Config


@contextmanager
def get_checkpointer():
    """
    Creates the LangGraph Postgres checkpointer.

    The import is kept inside the function so the backend can still
    start in environments where checkpointing is disabled.
    """
    if not Config.LANGGRAPH_CHECKPOINT_ENABLED:
        yield None
        return

    if not Config.DATABASE_URL:
        yield None
        return

    from langgraph.checkpoint.postgres import PostgresSaver

    with PostgresSaver.from_conn_string(
        Config.DATABASE_URL
    ) as checkpointer:
        checkpointer.setup()
        yield checkpointer