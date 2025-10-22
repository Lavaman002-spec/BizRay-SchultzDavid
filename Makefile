# BizRay Development Commands
# Usage: make <command>

.PHONY: help install dev clean backend frontend

help:
	@echo "BizRay Development Commands"
	@echo ""
	@echo "  make install   - Install all dependencies (frontend + backend)"
	@echo "  make dev       - Run both frontend and backend"
	@echo "  make backend   - Run backend only"
	@echo "  make frontend  - Run frontend only"
	@echo "  make clean     - Clean build artifacts and caches"

install:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo ""
	@echo "📦 Installing frontend dependencies..."
	cd frontend && pnpm install
	@echo ""
	@echo "✅ All dependencies installed!"

dev:
	@./dev.sh

backend:
	@echo "🚀 Starting backend on http://localhost:8000"
	cd backend && python server.py

frontend:
	@echo "🚀 Starting frontend on http://localhost:3000"
	cd frontend && pnpm dev

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf frontend/.next
	rm -rf frontend/out
	rm -rf backend/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned!"
