# BizRay Backend (FastAPI + ETL)

## Services

- **API** (FastAPI) – `/health`, `/companies/search`, `/companies/{id}`, `/companies/exports/{id}`
- **ETL** (run-once) – bulk & API ingestion → staging; normalization → canonical

## Env Vars

- `DATABASE_URL` e.g. `postgresql+psycopg://bizray:bizraypass@db:5432/bizray`
- `REGISTRY_API_BASE` – JustizOnline base URL
- `REGISTRY_API_KEY` – auth key
- `BULK_PATH` – folder with `companies.csv`, `officers.csv`, `links.csv` (default `/data/bulk`)

## Run locally (Docker)

Build & start from project root with docker-compose (see your root `docker-compose.yml`).

API: `http://localhost:8080/health`

## Run ETL once

Inside container:

```bash
python -m services.ingest.run_once
```
