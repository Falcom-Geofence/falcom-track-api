"""
Authentication endpoints for the Falcom Geofence API.

Provides routes for logging in using an employee ID and password, refreshing
access tokens, and fetching the current user. JWTs include the user ID and
role in the payload, enabling RBAC checks across the application.
"""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import auth as auth_utils
from ..db import get_db
from ..models import User
from ..schemas import Token, UserRead
from ..dependencies import get_current_user


class LoginRequest(BaseModel):
    employee_id: str
    password: str


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate a user and return an access and refresh token."""
    user: User | None = db.query(User).filter_by(employee_id=data.employee_id).first()
    if not user or not auth_utils.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid employee ID or password")
    # Build token payload
    payload = {"user_id": user.id, "role": user.role.value}
    access_token = auth_utils.create_access_token(payload)
    refresh_token = auth_utils.create_refresh_token(payload)
    return Token(access_token=access_token, refresh_token=refresh_token)


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest) -> Token:
    """Exchange a refresh token for a new access token."""
    try:
        payload = auth_utils.decode_token(data.refresh_token)
        # Ensure it is refresh by verifying expiry is longer; simply reuse payload
        user_id = payload.get("user_id")
        role = payload.get("role")
        if not user_id or not role:
            raise ValueError
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = auth_utils.create_access_token({"user_id": user_id, "role": role})
    refresh_token = auth_utils.create_refresh_token({"user_id": user_id, "role": role})
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user's information."""
    return current_user
