# Falcom Track API

This folder contains the FastAPI backend for the Falcom geofencing attendance system.

## Cloning this repository

To obtain this codebase on your local machine you can clone it from GitHub.  Use the following command:

```bash
git clone https://github.com/Falcom-Geofence/falcom-track-api.git
```

After cloning, change into the `falcom-track-api` directory to run the application or open it in your editor.

## Features

* **Health check** — exposes a `GET /health` endpoint returning `{"status": "ok"}`.  The admin dashboard and mobile app use this endpoint to verify that the service is running.
* - **Authentication & RBAC** – Employee ID + password login using bcrypt, with JWT access tokens (15 min) and refresh tokens (7 days). Roles (admin, manager, employee) enforce access control.
- **Sites API** – CRUD endpoints for geofence sites (`/sites`) with role-based permissions. Only admins can create, update and delete; managers can read, and employees have no access.
- **Automatic migrations** – Alembic automatically applies database migrations on startup.

* **Dockerised** — the API is packaged in a Dockerfile.  At runtime the container automatically runs Alembic migrations and starts the server with Uvicorn.
* **Database and cache ready** — the configuration assumes a PostgreSQL database and Redis cache are available on the same Docker network.  Alembic is configured but there are no migration scripts yet.
* **Swagger docs** — FastAPI automatically exposes interactive documentation at `/docs` and `/redoc`.

## Local development

1. Install the Python dependencies (Python 3.11+ is required):
   ```bash
   cd falcom-track-api
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a `.env` file by copying `.env.example` and update values as needed (e.g., `DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRE_MIN`, `JWT_REFRESH_EXPIRE_DAYS`, `CORS_ORIGINS`, and `TZ=Asia/Riyadh`).`postgresql+asyncpg://falcom:falcom@localhost:5432/falcom_track`).
3. Run any pending migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the application with Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Access the API docs at [http://localhost:8000/docs](http://localhost:8000/docs) and test endpoints such as `POST /auth/login` and `GET /auth/me`. The health check remains available at [http://localhost:8000/health](http://localhost:8000/health).

## Running with Docker

This project is designed to run inside Docker along with PostgreSQL and Redis.  When started in the `docker-compose` stack defined at the repository root, the backend container will:

1. Wait until the database and Redis containers are healthy.
2. Run Alembic migrations via `alembic upgrade head`.
3. Launch the FastAPI app on port 8000.

The relevant service is declared as `api` in `docker-compose.yml`.  To start everything, run `docker-compose up --build` from the repository root.

## Future work

Week 1 only requires a health‑check endpoint.  In later weeks you will add database models, authentication, and business logic.  Alembic and SQLAlchemy have been wired up so that adding tables and migrations will be straightforward.
