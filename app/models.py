"""
SQLAlchemy models for the Falcom Geofence API.

These models define the structure of the database tables. They include
convenient defaults such as creation timestamps and constraints like unique
indices. Roles are represented as an enumerated type on the User model.
"""

from __future__ import annotations

import datetime as dt
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum as SqlEnum,
    DateTime,
    Boolean,
    Float,
)

from .db import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    employee_id: str = Column(String(32), unique=True, nullable=False, index=True)
    full_name: str = Column(String(128), nullable=False)
    email: str | None = Column(String(256), nullable=True)
    role: UserRole = Column(SqlEnum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    password_hash: str = Column(String(256), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    created_at: dt.datetime = Column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc), nullable=False
    )


class Site(Base):
    __tablename__ = "sites"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(128), nullable=False)
    lat: float = Column(Float, nullable=False)
    lng: float = Column(Float, nullable=False)
    radius_m: float = Column(Float, default=150.0, nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    created_at: dt.datetime = Column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc), nullable=False
    )
