.PHONY: backend frontend dev

VENV := .venv
PYTHON := $(VENV)/bin/python

venv:
	@test -d $(VENV) || (echo "Creating virtual environment..." && python3 -m venv $(VENV) && $(PYTHON) -m pip install -r backend/requirements.txt)

backend: venv
	@echo "Starting backend..."
	@bash -c "$(PYTHON) backend/run.py"


frontend:
	@echo "Starting frontend..."
	@bash -c "cd frontend && npm run dev"

dev:
	@echo "Running bizray project..."
	@bash -c "trap 'kill 0' EXIT; $(PYTHON) backend/run.py & cd frontend && npm run dev"