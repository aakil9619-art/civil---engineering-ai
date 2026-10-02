# Civil Engineering AI

An exam-focused Civil Engineering learning platform for SSC JE, GATE CE and AE/JE preparation.

## Run it

Requirements: Python 3.10+.

```bash
git clone https://github.com/aakil9619-art/civil---engineering-ai.git
cd civil---engineering-ai
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Open **http://127.0.0.1:8000**.

## Current modules
- Civil topic bank covering 15 SSC JE technical subjects
- Original question generator with solutions and exam tips
- SSC JE mock-test flow
- Topic-wise performance analytics
- Diagram engine foundation
- Provider-neutral LLM integration
- Current/trending-topic ingestion contract

## Important
The LLM and current-affairs layers are intentionally provider-neutral. They do not claim live AI or live current-affairs data until a provider/source is configured and verified.
