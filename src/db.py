"""
Database connection and session management.
Connects to PostgreSQL via SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

_engine = None
_Session = None


def init_db(database_url: str = "postgresql://localhost:5432/taskly"):
    global _engine, _Session
    _engine = create_engine(database_url)
    Base.metadata.create_all(_engine)
    _Session = sessionmaker(bind=_engine)


def get_db_session():
    return _Session()
