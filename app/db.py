"""
Database setup and session management for the Falcom Geofence API.

This module defines the SQLAlchemy engine, session factory and base class used
throughout the application. It reads the `DATABASE_URL` from the environment
and configures SQLAlchemy accordingly. A dependency is also provided for
retrieving a scoped session in FastAPI routes.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Read database URL from environment; fall back to a sane default if unset.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://falcom:falcom@localhost:5432/falcom",
)

# SQLAlchemy engine and session factory.
engine = create_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Declarative base class for models.
Base = declarative_base()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Yield a new database session for a request and ensure it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
