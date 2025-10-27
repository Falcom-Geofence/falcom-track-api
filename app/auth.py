"""
Authentication utilities for the Falcom Geofence API.

This module centralises password hashing and JSON Web Token creation and
verification. It uses passlib's bcrypt scheme for secure password storage and
python-jose for signing JWTs. The JWT includes the user's ID and role in its
payload to facilitate role-based access control downstream.
"""

from __future__ import annotations

import datetime as dt
import os
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .models import User, UserRole

# Cryptographic context for bcrypt hashing.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Read JWT configuration from environment or fallback defaults.
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME_FALCOM_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MIN", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the given plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash the given password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[dt.timedelta] = None) -> str:
    """Generate a signed JWT containing the given data and an expiry."""
    to_encode = data.copy()
    expire = dt.datetime.utcnow() + (
        expires_delta
        if expires_delta
        else dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Generate a refresh token with a longer expiry."""
    expire = dt.datetime.utcnow() + dt.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT and return its payload. Raise JWTError if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise exc


def authenticate_user(user: User, password: str) -> bool:
    """Return True if the provided password is valid for the user."""
    return verify_password(password, user.password_hash)
