from fastapi import FastAPI

app = FastAPI(title="Civil Engineering AI")

@app.get("/health")
def health():
    return {"status": "ok"}
