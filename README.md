
# Medical Coding Automation

AI-assisted tool that analyzes free-text clinical notes and suggests ICD-10 diagnosis codes and CPT/HCPCS procedure codes with confidence scores and explanations, using semantic search over the code descrip
tions.

See [`docs/problem_statement.md`](docs/problem_statement.md) for the motivating problem.

## Architecture

- **`backend/`** — FastAPI service.
  - `app/rag/vector_store.py` embeds ICD-10 and CPT descriptions with `sentence-transformers` (`all-MiniLM-L6-v2`) and indexes them in FAISS for nearest-neighbor lookup.
  - `app/rag/index_cache.py` builds the two vector stores once per process and caches them in memory.
  - `app/agents/analyzer_agent.py` searches the ICD-10 store for every note, and the CPT store only when a procedure keyword (x-ray, MRI, biopsy, etc.) is present in the text, filtering to matches with confidence >= 75.
  - `app/agents/validator_agent.py` runs rule-based sanity checks (missing diagnosis, missing procedure, low confidence) and returns warnings.
  - `app/agents/explanation_agent.py` attaches a human-readable explanation to each suggested code.
  - `app/utils/csv_loader.py` loads the prepared datasets from `datasets/`.
  - `backend/scripts/` are one-time ETL scripts that turn raw CMS/HCPCS source files in `datasets/raw/` into the `datasets/icd10_codes.csv` and `datasets/cpt_codes.csv` files the app reads at runtime.
- **`frontend/`** — React (Vite) + Tailwind single-page app. A textarea posts clinical notes to `POST /analyze-text` and renders the returned ICD-10 codes, CPT codes, confidence bars, explanations, and any validator warnings.
- **`datasets/`** — CSV code reference data consumed by the backend. `cpt_codes.csv` is currently a small placeholder set (HCPCS behavioral-health codes), not a full CPT code set.

## Running locally

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API runs at `http://127.0.0.1:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173` and expects the backend at `http://127.0.0.1:8000`.

## Known limitations

- `datasets/cpt_codes.csv` is a placeholder (27 HCPCS rows), not a real CPT procedure code set.
- Each analysis returns at most one ICD-10 code and one CPT code per note (`top_k=1` in `VectorStore.search`).
- FAISS index is rebuilt in memory on every backend restart — it is not persisted to disk.
- No authentication, database, or persistence of past analyses.
- No automated tests yet.
