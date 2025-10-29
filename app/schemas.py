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
    ConfigDict = dict  # fallback if needed

from .models import UserRole


# ========== AUTH ==========
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


# ========== USERS ==========
class UserBase(BaseModel):
    employee_id: str
    full_name: str
    email: Optional[EmailStr] = None
    role: UserRole
    is_active: bool = True
    created_at: Optional[dt.datetime] = None  # read-only


class UserCreate(BaseModel):
    employee_id: str
    full_name: str
    password: str
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.employee  # enums are lowercase: admin/manager/employee


class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ========== SITES ==========
class SiteBase(BaseModel):
    name: str            # نُبقيها كما هي الآن (بدون AR/EN) عشان ما نكسر الجداول الحالية
    lat: float
    lng: float
    radius_m: float = 150.0
    is_active: bool = True
    created_at: Optional[dt.datetime] = None  # read-only


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
    model_config = ConfigDict(from_attributes=True)


# ========== TRACKING ==========
class TrackingPointBase(BaseModel):
    employee_id: str
    timestamp: dt.datetime
    lat: float
    lng: float
    accuracy: Optional[float] = None
    site_id: Optional[int] = None
    site_name_ar: Optional[str] = None
    site_name_en: Optional[str] = None
    created_at: Optional[dt.datetime] = None  # read-only


class TrackingPointCreate(BaseModel):
    employee_id: str
    # نخلي التايم ستامب اختياري؛ لو ما انبعت من العميل بنحطه الآن في الراوتر/الخدمة
    timestamp: Optional[dt.datetime] = None
    lat: float
    lng: float
    accuracy: Optional[float] = None


class TrackingPointRead(TrackingPointBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
