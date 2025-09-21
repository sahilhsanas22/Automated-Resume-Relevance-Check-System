# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project summary
- AI-powered resume evaluation system with a Streamlit frontend and a FastAPI backend.
- SQLite for transactional data, ChromaDB for vector search. Optional LLM features enabled by OPENAI_API_KEY.

Common commands (PowerShell on Windows)
- Setup (create venv and install deps)
```powershell path=null start=null
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Run Streamlit UI (port 8501)
```powershell path=null start=null
python -m streamlit run app/web/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

- Run FastAPI backend (port 8000, reload)
```powershell path=null start=null
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

- Run full system (starts FastAPI + Streamlit, auto-installs spaCy model if missing)
```powershell path=null start=null
python .\run_system.py
```

- Optional: install spaCy English model manually (if needed)
```powershell path=null start=null
python -m spacy download en_core_web_sm
```

- Health check and example API calls
```powershell path=null start=null
# Health
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET | ConvertTo-Json -Depth 5

# List jobs
Invoke-RestMethod -Uri "http://localhost:8000/jobs/" -Method GET | ConvertTo-Json -Depth 5

# Create a job (example)
$body = @{ title = "Backend Engineer"; jd_text = "Python, FastAPI"; must_skills = @("python","fastapi"); nice_skills = @("docker"); location = "Remote" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/jobs/" -Method POST -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 5
```

- Enabling LLM features (OpenAI)
```powershell path=null start=null
# Set before starting the app
$env:OPENAI_API_KEY = "{{OPENAI_API_KEY}}"
```

- Data locations (created on first run)
  - SQLite database: data/app.db
  - ChromaDB persistence: data/chroma_db

Notes on tests and linting
- No test suite or linter configuration is present in this repository.

High-level architecture and flow
- Frontend (Streamlit): app/web/streamlit_app.py
  - Pages: Upload JD, Upload Resume, Dashboard.
  - Directly uses the shared database/session and services; provides rich visualizations (Plotly) and status panels.
- Backend (FastAPI): app/api/main.py
  - REST endpoints for job management, resume evaluation, semantic search, and analytics.
  - CORS is permissive by default; adjust for production.
- Services layer: app/services/
  - evaluator.py: Orchestrates the hybrid scoring pipeline and persists Evaluation rows.
  - llm_evaluator.py: Optional LLM-powered analysis via LangChain; always-on Chroma vector store for semantic search.
- NLP layer: app/nlp/
  - advanced_processor.py: spaCy+NLTK entity extraction and text stats with graceful fallbacks.
  - scoring.py: Hard match (keyword/fuzzy) + soft match (embeddings or TF-IDF) + weighted blend.
  - embeddings.py: Sentence-Transformers embeddings with TF-IDF fallback.
- Parsing layer: app/parsing/
  - files.py: PDF/DOCX extraction and normalization.
  - jd_parser.py: Heuristic skill extraction from freeform JDs.
- Persistence: app/db/
  - SQLAlchemy models (Job, Resume, Evaluation) and CRUD. Tables created on import; SQLite path from app/config.py.

End-to-end data flow (big picture)
1) Job Description intake
   - Source: UI (manual or file upload) or API (/jobs/, /jobs/upload).
   - Skills parsed (heuristics) and saved; JD text embedded and added to Chroma for semantic search.
2) Resume intake and evaluation
   - Source: UI upload or API (/evaluate/).
   - Text extraction (PDF/DOCX) and normalization.
   - Hybrid scoring: hard_match_score (keyword/fuzzy) + soft_match_score (embeddings/TF-IDF) → weighted_score.
   - Optional LLM pass (if OPENAI_API_KEY present) refines semantic score, gaps, strengths, and suggestions.
   - Entity extraction augments missing-skill checks; result persisted as Evaluation.
3) Analytics and search
   - Vector search via Chroma (semantic queries over resumes/JDs).
   - Aggregates for dashboard via /analytics/dashboard and Streamlit charts.

Key configuration (app/config.py)
- Weights and thresholds: HARD_MATCH_WEIGHT, SOFT_MATCH_WEIGHT, VERDICT_THRESHOLDS.
- Embedding behavior: EMBEDDINGS_MODEL, USE_EMBEDDINGS (True for ST; False to force TF-IDF).
- App name and DB path: APP_NAME, DB_PATH.

Important URLs (local)
- Streamlit UI: http://localhost:8501
- FastAPI docs (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/health

Repository-specific considerations
- The Streamlit app and FastAPI backend share the same database and vector store; you can run either independently or together via run_system.py.
- NLTK resources and spaCy model are fetched at runtime if missing; first run may take longer.
