"""
Pydantic models defining request and response shapes for the API.

These schemas enforce data validation and document the API responses via
FastAPI's automatic OpenAPI generation. Fields for reading and writing are
separated where appropriate (e.g. password input vs hashed password output).
"""

from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field, EmailStr
try:
    # Pydantic v2
    from pydantic import ConfigDict
except ImportError:
    ConfigDict = dict  # fallback (won't be used with v2)

from .models import UserRole


# ===== Auth =====
class LoginRequest(BaseModel):
    employee_id: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer", description="The type of token")


class TokenData(BaseModel):
    user_id: int
    role: UserRole
    exp: Optional[int] = None


# ===== User =====
class UserBase(BaseModel):
    employee_id: str
    full_name: str
    email: Optional[EmailStr] = None
    role: UserRole
    is_active: bool = True
    created_at: Optional[dt.datetime] = None  # read-only in practice


class UserCreate(BaseModel):
    employee_id: str
    full_name: str
    password: str
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.employee  # enums are lowercase: admin/manager/employee


class UserRead(UserBase):
    id: int
    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)


# ===== Site =====
class SiteBase(BaseModel):
    name: str
    lat: float
    lng: float
    radius_m: float = 150.0
    is_active: bool = True
    created_at: Optional[dt.datetime] = None  # read-only in practice


class SiteCreate(BaseModel):
    name: str
    lat: float
    lng: float
    radius_m: float = 150.0


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_m: Optional[float] = None
    is_active: Optional[bool] = None


class SiteRead(SiteBase):
    id: int
    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)
