from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import settings


def get_engine() -> Engine:
    return create_engine(settings.database_url, pool_pre_ping=True)


def check_database_connection(engine: Engine | None = None) -> bool:
    eng = engine or get_engine()
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
