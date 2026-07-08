# Fake News Detection — Prototype

This workspace contains a prototype FastAPI backend for a Fake News Detection project. It provides endpoints to analyze submitted text or images (via OCR) with a small TF-IDF+LogisticRegression classifier trained on toy data.

Quick start
-----------
1. Create and activate a virtual environment (optional but recommended).

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.\\\venv\\\Scripts\\\Activate.ps1  # Windows PowerShell
```

2. Install requirements:

```bash
pip install -r requirements.txt
```

3. (Optional) Install Tesseract OCR on your system for image OCR. On Windows, download from: https://github.com/tesseract-ocr/tesseract

4. Train the demo model:

```bash
python backend/scripts/train_model.py
```

5. Run the API:

```bash
uvicorn backend.app.main:app --reload
```

Endpoints
---------
- `POST /predict/text` — form field `text` (string). Returns `label` and `score`.
- `POST /predict/image` — multipart file `file` (image). Extracts text using OCR then predicts.

- Frontend: a Vite + React + Tailwind UI is scaffolded under `frontend/`. To run it:

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000` by default. You can set a different backend base by creating a `.env` file in `frontend/` with `VITE_API_BASE`.

Verification script
-------------------
To quickly verify the running backend endpoints, run:

```bash
python backend/scripts/verify_endpoints.py
```

This script will POST a sample text and a generated image containing text to the API and print the results.

Notes
-----
- This is a prototype with toy data. Replace training data and improve the local fact-checking heuristics for production use.
- The workspace includes `.env.example` to configure your Gemini API key for future integrations.

Completed extras
----------------
- Transformer zero-shot endpoint: `POST /predict/text/transformer` (uses Hugging Face zero-shot pipeline).
- Unit tests: `backend/tests/test_api.py` (mocks heavy components where appropriate).
- CI workflow: `.github/workflows/ci.yml` runs pytest on push/PR.
- Dockerfiles: `backend/Dockerfile` and `frontend/Dockerfile` for containerized deployment.
