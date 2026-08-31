from contextlib import contextmanager
from typing import Any
from langgraph.checkpoint.memory import MemorySaver

from config import Config


@contextmanager
def get_checkpointer():
    """
    Creates the LangGraph checkpointer.
    Uses PostgresSaver if PostgreSQL is reachable,
    otherwise falls back to MemorySaver.
    """
    if not Config.LANGGRAPH_CHECKPOINT_ENABLED:
        yield None
        return

    conn_string = (Config.DATABASE_URL or "").replace("postgresql+psycopg://", "postgresql://")

    if conn_string.startswith("postgresql://"):
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            from psycopg import connect

            # Test connection first before compiling
            with connect(conn_string, connect_timeout=3) as conn:
                saver = PostgresSaver(conn)
                saver.setup()
                yield saver
                return
        except Exception:
            pass

    # Safe fallback to MemorySaver for robust graph execution
    yield MemorySaver()