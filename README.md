# PLAGIARISM-CHECK

A small web application and analysis pipeline for detecting document plagiarism using several techniques (suffix trees, bloom filters, semantic similarity and web search). This repository contains a Python backend that runs the detection pipeline and a React frontend for uploading documents and viewing results.

## Table of Contents
- [Project overview](#project-overview)
- [Key features](#key-features)
- [Repository layout](#repository-layout)
- [Tech stack](#tech-stack)
- [Quick start (Windows / PowerShell)](#quick-start-windows--powershell)
    - [Backend setup & run](#backend-setup--run)
    - [Frontend setup & run](#frontend-setup--run)
- [How to use](#how-to-use)
- [Data layout and where to add documents](#data-layout-and-where-to-add-documents)
- [Development notes](#development-notes)
- [Contributing](#contributing)
- [License & contact](#license--contact)

## Project overview

This project provides a plagiarism detection system that:

- Accepts document uploads via a React frontend.
- Runs multiple detection strategies in the Python backend (local corpus comparison, suffix-tree matching, bloom-filter heuristics, semantic similarity, and optional web search of the internet for matches).
- Returns match results with context and similarity scores for inspection.

The aim is to provide a balanced pipeline that combines exact-match algorithms (fast) with semantic checks (robust to paraphrasing).

## Key features

- File upload UI (frontend).
- Suffix-tree based substring matching.
- Bloom filter checks for quick presence/absence heuristics.
- Semantic similarity (NLP) to detect paraphrases.
- Web search + content extraction (optional, configurable) for checking online sources.

## Repository layout

Top-level files and directories (important ones):

- `backend/` — Python backend and detection pipeline
    - `app.py` — Flask (or script) entry point for the backend API/service
    - `requirements.txt` — Python dependencies
    - `bloom_filter/`, `suffix_tree/`, `nlp_similarity/`, `pipeline/`, `preprocessing/`, `web_search/`, `utils/` — implementation modules
    - `data/` — storage for indexes, reference docs, uploads, temp files
- `frontend/` — React application (create-react-app style)
    - `src/` — React source code (components include `FileUploadForm.js`, `ResultsDisplay.js`, `MatchesList.js`)
    - `package.json` — frontend dependency manifest

## Tech stack

- Backend: Python (Flask or simple HTTP server). Core detection code in Python modules in `backend/`.
- Frontend: React (JavaScript), in `frontend/`.

## Quick start (Windows / PowerShell)

Below are minimal steps to run the project locally on Windows (PowerShell). These assume you have Python 3.8+ and Node.js installed.

### Backend setup & run

Open PowerShell and run:

```powershell
cd C:\Users\Admin\Desktop\is1_project
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r backend\requirements.txt
python backend\app.py
```

Notes:
- If `app.py` uses Flask app.run, the command above will start the backend. If the backend is configured to run with `flask run`, you can alternatively set FLASK_APP and run `flask run`.
- Backend configuration values (API keys, web-search toggles) can be found/edited in `backend/config.py`.

### Frontend setup & run

Open a separate PowerShell window and run:

```powershell
cd C:\Users\Admin\Desktop\is1_project\frontend
npm install
npm start
```

This will start the React development server (usually at http://localhost:3000). The frontend will communicate with the backend API — if the backend runs on a different port, update the frontend API base URL (search for `fetch` or the API client in `src/`).

## How to use

1. Start backend and frontend as described above.
2. Open the frontend in your browser (http://localhost:3000 by default).
3. Use the upload form to submit a document (or place files into `backend/data/uploads/` and use the UI to point to them).
4. Wait for the pipeline to run; results will show matched fragments, scores and sources (local or web).

## Data layout and where to add documents

- `backend/data/reference_docs/` — place reference documents (corpus) you want to check against.
- `backend/data/indexes/` — precomputed indexes created by the backend (suffix-tree indexes, etc.).
- `backend/data/uploads/` — incoming uploaded files stored here.
- `backend/data/temp/` — transient files used during processing.

If you add a large corpus, consider running any indexing scripts (if present) in `backend/` to rebuild indexes for faster matching.

## Development notes

- The pipeline combines multiple signals; you can find separate modules under `backend/`:
    - `suffix_tree/suffix_tree.py` — longest-common-substring/match extraction logic.
    - `bloom_filter/bloom_filter.py` — quick set-membership checks.
    - `nlp_similarity/semantic_similarity.py` — sentence / embedding-based similarity.
    - `web_search/` — web querying and content extraction.

- Configuration is centralized in `backend/config.py` — toggle web search, set API keys, adjust thresholds.

## Contributing

1. Fork and create a branch for your feature or fix.
2. Run tests (frontend) and linting locally.
3. Create a PR with clear description and test steps.

## License & contact

This repo doesn't include an explicit license file; add one if you plan to share the project publicly (MIT is a permissive option).

If you want me to expand this README with API endpoint docs (e.g., exact upload endpoint, request/response examples) I can extract them directly from `backend/app.py` and add a dedicated API section.

---

Small verified checklist:

- [x] README content updated with clear setup instructions
- [ ] Add explicit API examples (optional — I can extract them next)

Happy hacking — if you'd like, I can also:

- Add API docs (automatic extraction from `backend/app.py`).
- Add a small example `curl` or PowerShell request demonstrating the upload endpoint.

