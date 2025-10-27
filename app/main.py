from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance
app = FastAPI(title="Falcom Track API")

# Allow CORS so that the web dashboard and mobile app can call the API.
# In a production system you would want to restrict this to trusted domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def read_health():
    """
    Simple health‑check endpoint used by the web dashboard and mobile app to
    verify that the backend is up and running.  It returns a JSON object
    containing a single field called ``status`` set to ``ok``.
    """
    return {"status": "ok"}
