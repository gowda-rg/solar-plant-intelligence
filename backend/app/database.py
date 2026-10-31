# =============================================================================
# WORKFLOW — shared database access for Phase 1–2
# =============================================================================
# config.settings.database_url  ← backend/.env (DATABASE_URL)
# check_database_connection()   ← Phase 1 /health/db, pytest
# create_schema()               ← Phase 2a init_db.py
# get_db() / get_session_factory() ← Phase 2b seed, Phase 2d API routes
# MAP: scripts/seed_demo_data.py PROJECT WORKFLOW MAP
# =============================================================================
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Base

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def check_database_connection(engine: Engine | None = None) -> bool:
    eng = engine or get_engine()
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True


def create_schema(engine: Engine | None = None) -> None:
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)
