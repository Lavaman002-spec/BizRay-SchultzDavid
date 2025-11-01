SHELL := /bin/bash

.PHONY: up down etl logs rebuild

up:
	@echo "🚀 Starting full Bizray stack..."
	docker compose up --build

down:
	@echo "🧹 Stopping and removing containers..."
	docker compose down -v

etl:
	@echo "📦 Running ETL pipeline once..."
	docker compose run --rm etl_once

logs:
	docker compose logs -f api_service

rebuild:
	@echo "♻️ Rebuilding all images..."
	docker compose build --no-cache
