# Bulk Data Setup for BizRay

## Overview

BizRay is configured to automatically load bulk company data from CSV files when the application starts. This ensures users have immediate access to company data without waiting for API fetches.

## Current Status

✅ **231 companies** are currently available in CSV files
✅ **558 officers** are currently available in CSV files
✅ CSV files are stored in `backend/data/`
✅ Automatic loading on app startup is configured

## CSV Files

The following CSV files are used for bulk loading:

1. **companies.csv** (10 KB, 231 companies)

   - Format: `register_id,name,city,status`
   - Contains real Austrian company data

2. **officers.csv** (29 KB, 558 officers)

   - Format: `company_register_id,person_name,role`
   - Contains company officers and their roles

3. **links.csv** (43 B, 0 links)
   - Format: `from_register_id,to_register_id,link_type`
   - Currently empty (ownership links will be added later)

## How It Works

### Automatic Loading on Startup

When you run `docker-compose up`, the `etl_once` service automatically:

1. Waits for the database to be ready
2. Initializes the database schema
3. Loads CSV files from `backend/data/` into staging tables
4. Runs normalization to populate canonical tables
5. Exits (one-time operation)

This happens automatically before the API service starts, so users immediately have access to company data.

### Manual Export/Import

#### Export Current Database to CSV

To export the current database to CSV files (useful after fetching more companies):

```bash
cd backend/services/ingest
python export_to_csv.py
```

This will:

- Export all companies to `backend/data/companies.csv`
- Export all officers to `backend/data/officers.csv`
- Export all links to `backend/data/links.csv`

#### Fetch More Companies from API

To fetch additional companies and add them to CSV files:

```bash
cd backend/services/ingest

# Fetch 100 companies
python run_bulk_ingest.py --max 100

# Export to CSV
python export_to_csv.py

# Move files to correct location
mv ../services/data/*.csv ../data/
```

#### Reach 1000 Companies

To populate the CSV files with ~1000 companies:

```bash
cd backend/services/ingest

# Option 1: Fetch all at once (takes 20-30 minutes)
python run_bulk_ingest.py --max 1000

# Option 2: Fetch in batches
python run_bulk_ingest.py --max 200  # ~5 minutes
python run_bulk_ingest.py --max 200  # ~5 minutes
python run_bulk_ingest.py --max 200  # ~5 minutes
python run_bulk_ingest.py --max 200  # ~5 minutes
python run_bulk_ingest.py --max 200  # ~5 minutes

# Export to CSV after fetching
python export_to_csv.py
mv ../services/data/*.csv ../data/
```

## Testing

### Test CSV Loading

To test that CSV files are loaded correctly:

```bash
# Start fresh (deletes existing data)
docker-compose down -v
docker-compose up -d db
docker-compose up etl_once

# Check logs
docker logs bizray-etl_once

# Verify data was loaded
docker exec bizray-db psql -U postgres -d bizray -c "SELECT COUNT(*) FROM companies;"
```

### Test API

```bash
# Start API service
docker-compose up -d api_service

# Search for companies
curl "http://localhost:8080/companies/search?q=wolfinger"
```

## Configuration

### Docker Compose

The `etl_once` service in `docker-compose.yml`:

```yaml
etl_once:
  build:
    context: ./backend
    dockerfile: Dockerfile
  container_name: bizray-etl_once
  environment:
    - POSTGRES_HOST=db # Critical: connects to db container
    - POSTGRES_USER=${POSTGRES_USER}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    - POSTGRES_DB=${POSTGRES_DB}
  volumes:
    - ./backend:/bizray/backend # Mounts CSV files
  depends_on:
    db:
      condition: service_healthy
  command: ['python', '-m', 'services.ingest.etl.run_once']
```

### Bulk Ingest Paths

The `bulk_ingest.py` script looks for CSV files in these locations (in order):

1. `backend/data/` (primary location)
2. `/bizray/backend/data` (Docker path)
3. `backend/data/bulk/` (fallback)
4. `/app/data` (legacy Docker path)

## Files

- `backend/data/companies.csv` - Company data
- `backend/data/officers.csv` - Officer data
- `backend/data/links.csv` - Ownership links
- `backend/services/ingest/export_to_csv.py` - Export script
- `backend/services/ingest/populate_csv_data.py` - Fetch and populate script
- `backend/services/ingest/etl/run_once.py` - Startup loader
- `backend/services/ingest/etl/bulk_ingest.py` - CSV ingestion logic

## Troubleshooting

### CSV Files Not Loading

Check:

1. Files exist: `ls -lh backend/data/*.csv`
2. Files have data: `wc -l backend/data/*.csv`
3. Container can access files: `docker exec bizray-etl_once ls -la /bizray/backend/data/`

### etl_once Container Fails

Check logs:

```bash
docker logs bizray-etl_once
```

Common issues:

- Database not ready: Wait for `bizray-db` to be healthy
- Missing POSTGRES_HOST: Should be `db` not `localhost`
- Permission errors: Check file permissions on CSV files

### Zero Companies After Loading

1. Check if CSV files were actually loaded:

   ```bash
   docker exec bizray-db psql -U postgres -d bizray -c "SELECT COUNT(*) FROM stg_companies;"
   ```

2. Check if normalization ran:
   ```bash
   docker exec bizray-db psql -U postgres -d bizray -c "SELECT COUNT(*) FROM companies;"
   ```

## Next Steps

To reach the goal of ~1000 companies:

1. **Fetch more companies**: Run `python run_bulk_ingest.py --max 800`
2. **Export to CSV**: Run `python export_to_csv.py` and move files
3. **Restart app**: `docker-compose down && docker-compose up -d`
4. **Verify**: Check that frontend shows ~1000 companies available

The bulk ingestion takes approximately:

- 200 companies: ~5-8 minutes
- 500 companies: ~12-20 minutes
- 1000 companies: ~25-35 minutes

API rate limiting: ~0.5-1 second delay between requests to avoid overloading the Austrian Business Register API.
