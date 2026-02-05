"""
SQLAlchemy base configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries (useful for debugging)
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_session():
    """
    Get a database session.

    Usage:
        with get_session() as session:
            routes = session.query(Route).all()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db():
    Base.metadata.create_all(bind=engine)


def drop_all():
    Base.metadata.drop_all(bind=engine)
