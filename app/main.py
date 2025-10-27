"""
Entry point for the Falcom Geofence API.

This module configures the FastAPI application, adds CORS and timezone
configuration, includes routers for authentication and site management, and
seeds the database with an initial administrator and a handful of placeholder
sites on startup. Health check endpoint is also provided.
"""

from __future__ import annotations

import asyncio
import os
from typing import Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .db import Base, engine, get_db
from .models import User, UserRole, Site
from .auth import get_password_hash
from .routers import auth as auth_router, sites as sites_router


def create_app() -> FastAPI:
    app = FastAPI(title="Falcom Track API")
    # Read CORS origins from environment. Accept comma separated list.
    origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    origins: Iterable[str] = [o.strip() for o in origins_env.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router.router)
    app.include_router(sites_router.router)

    @app.get("/health", tags=["Utility"])
    async def read_health() -> dict[str, str]:
        """Return a simple status message indicating the API is reachable."""
        return {"status": "ok"}

    @app.on_event("startup")
    async def on_startup() -> None:
        """Create tables and seed initial data if necessary."""
        # Create database tables
        Base.metadata.create_all(bind=engine)
        # Seed admin user and default sites synchronously in a threadpool
        def seed():
            from sqlalchemy.orm import Session
            with get_db() as db:
                # Seed admin user
                admin_emp_id = "220220"
                admin_user: User | None = db.query(User).filter_by(employee_id=admin_emp_id).first()
                if admin_user is None:
                    admin_user = User(
                        employee_id=admin_emp_id,
                        full_name="Haytham Waheed",
                        role=UserRole.ADMIN,
                        password_hash=get_password_hash("Falcom@123"),
                        email=None,
                        is_active=True,
                    )
                    db.add(admin_user)
                # Seed placeholder sites only if none exist
                if db.query(Site).count() == 0:
                    placeholder_sites = [
                        Site(name="Headquarters", lat=24.7136, lng=46.6753, radius_m=150.0),
                        Site(name="Warehouse", lat=24.7250, lng=46.6500, radius_m=150.0),
                        Site(name="Remote Office", lat=24.7000, lng=46.6900, radius_m=150.0),
                    ]
                    db.add_all(placeholder_sites)
                db.commit()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, seed)

    return app


app = create_app()
