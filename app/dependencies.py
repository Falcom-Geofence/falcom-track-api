"""
FastAPI dependencies for database access, authentication and RBAC.

This module exposes dependency functions used in route definitions. They
abstract common concerns such as loading a database session, extracting the
current user from a JWT bearer token and enforcing role-based permissions.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from .auth import decode_token
from .db import get_db
from .models import User, UserRole

# OAuth2 scheme that reads the bearer token from the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Return the current user based on the given JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: int | None = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        role = payload.get("role")
    except JWTError:
        raise credentials_exception
    user: User | None = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_roles(*roles: UserRole):
    """
    Factory that returns a dependency verifying the current user has one of
    the specified roles. Use like: Depends(require_roles(UserRole.ADMIN)).
    """

    def role_checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return role_checker
