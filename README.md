
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
  - `app/agents/explanation_agent.py` attaches a templated human-readable explanation to each suggested code (the default, always-available path).
  - `app/agents/llm_agent.py` optionally replaces that with an LLM-generated clinical justification when `ANTHROPIC_API_KEY` is set; falls back to the templated explanation automatically if the key is absent or the call fails.
  - `app/db.py` persists every analysis as a `sessions` row and each suggested code as a `code_reviews` row (SQLite, `backend/coding_reviews.db`, gitignored) — the human-in-the-loop audit trail described below.
  - `app/utils/csv_loader.py` loads the prepared datasets from `datasets/`.
  - `app/utils/file_extractor.py` extracts text from uploaded PDFs and images: native text extraction for born-digital PDFs (PyMuPDF), with an OCR fallback (pytesseract) for scanned PDF pages and image files. Exposed via `POST /extract-text`.
  - `backend/scripts/` are one-time ETL scripts that turn raw CMS/HCPCS source files in `datasets/raw/` into the `datasets/icd10_codes.csv` and `datasets/cpt_codes.csv` files the app reads at runtime.
- **`frontend/`** — React (Vite) + Tailwind single-page app. A textarea posts clinical notes to `POST /analyze-text` and renders the returned ICD-10 codes, CPT codes, confidence bars, explanations, and any validator warnings. Notes can also be loaded from a PDF or image via the file upload control, which fills the textarea with the extracted text for review before analysis. Each suggested code has Approve/Reject buttons that call the review endpoint below.
- **`datasets/`** — CSV code reference data consumed by the backend. `cpt_codes.csv` is currently a small placeholder set (HCPCS behavioral-health codes), not a full CPT code set.

## Human-in-the-loop review

`POST /analyze-text` creates a `session` and one `code_review` row per suggested code (status `pending`) before returning the response, so every suggestion is persisted the moment it's made, not just when a human acts on it. The coder then approves or rejects each one:

- `POST /reviews/{review_id}/decision` — body `{"status": "approved"}` or `{"status": "rejected"}`, updates that code's review row with a timestamp.
- `GET /sessions/{session_id}` — returns the original note plus every code review and its current status, for audit/history purposes.

No code is deleted or auto-finalized on rejection — the row is kept with `status = "rejected"` so the full decision trail is preserved.

## Optional: LLM-generated explanations

By default, explanations come from a fixed template (`explanation_agent.py`). Setting `ANTHROPIC_API_KEY` in the environment switches to `llm_agent.py`, which asks an LLM to judge whether the retrieved code is actually supported by the note and to quote the supporting phrase — a real reasoning step instead of a template. It only reasons over codes the RAG step already retrieved (it cannot introduce codes outside the dataset), and any failure (missing key, network error, rate limit) falls back to the template silently.

```bash
# backend/.env or your shell
ANTHROPIC_API_KEY=sk-ant-...
```

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

### OCR engine (optional, for scanned PDFs and images)

Uploading a native (text-based) PDF works out of the box. Extracting text from a scanned PDF page or an image file requires the Tesseract OCR engine to be installed separately (it is a system binary, not a Python package):

- Windows: install via the [UB Mannheim Tesseract build](https://github.com/UB-Mannheim/tesseract/wiki) or `choco install tesseract` (run from an elevated shell), then ensure `tesseract.exe` is on your `PATH`.
- macOS: `brew install tesseract`
- Linux: `apt install tesseract-ocr` (or your distro's equivalent)

Without it, `/extract-text` still works for text-based PDFs and returns a clear `503` error only when OCR would actually be needed.

## Known limitations

- `datasets/cpt_codes.csv` is a placeholder (27 HCPCS rows), not a real CPT procedure code set.
- Each analysis returns at most one ICD-10 code and one CPT code per note (`top_k=1` in `VectorStore.search`).
- FAISS index is rebuilt in memory on every backend restart — it is not persisted to disk.
- No authentication or multi-user support — the SQLite review log has no concept of who approved/rejected a code.
- No automated tests yet.
