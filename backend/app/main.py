from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .api import router
from .subjects import SUBJECTS, EXAM_PROFILES

app = FastAPI(title="Civil Engineering AI", version="0.2.0")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "civil-engineering-ai"}

@app.get("/api/subjects")
def subjects():
    return {"subjects": SUBJECTS, "exam_profiles": EXAM_PROFILES}

# Serve the browser app from the same FastAPI process.
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
