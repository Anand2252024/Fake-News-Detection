PY=python

.PHONY: install deps train run-backend run-tests build-images up

install:
	$(PY) -m venv .venv
	.venv\Scripts\Activate.ps1 && pip install -r requirements.txt

train:
	$(PY) backend/scripts/train_model.py

run-backend:
	$(PY) -m uvicorn backend.app.main:app --reload

run-tests:
	pytest -q

build-images:
	docker-compose build

up:
	docker-compose up --build
