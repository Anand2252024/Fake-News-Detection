# Fake News Detection — Release Notes

Version: 0.1.0 (prototype)

Features
- FastAPI backend with TF-IDF demo classifier and transformer zero-shot endpoint.
- OCR text extraction pipeline (requires Tesseract binary for image OCR).
- Local heuristic fact-check helper (Bing API removed).
- React + Vite + Tailwind frontend with polished UI scaffold.
- Unit tests with `pytest` and a CI workflow at `.github/workflows/ci.yml`.
- Dockerfiles for backend and frontend and `docker-compose.yml` for local deployment.

Getting started
- See `README.md` for full setup instructions.

Notes
- The transformer zero-shot endpoint downloads a model on first use; ensure network and sufficient memory.
- Replace toy training data in `backend/data/sample_train.csv` with labeled data for production.
