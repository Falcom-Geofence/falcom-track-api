# Use a slim Python base image
FROM python:3.11-slim as base

# Prevent Python from generating .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Expose the port FastAPI will listen on
EXPOSE 8000

# The default command runs database migrations and then starts the API.
["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
#CMD ["sh","-c","alembic upgrade head || echo 'no migrations'; uvicorn app.main:app --host 0.0.0.0 --port 8000"]
