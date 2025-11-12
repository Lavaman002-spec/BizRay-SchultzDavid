# Company Data Ingestion

This directory contains tools for fetching company data from the Austrian Firmenbuch API and storing it in Supabase.

## Files

- **`api_client.py`** - Low-level SOAP API client for Firmenbuch
- **`api_fetch.py`** - High-level functions for fetching and persisting company data
- **`bulk_upload.py`** - Script for bulk importing companies from CSV or FNR ranges

## Bulk Upload Tool

The `bulk_upload.py` script provides three modes for importing companies:

### 1. Import from CSV File (Recommended)

The most efficient method if you have a list of known company FNRs or names.

**CSV Format Options:**

CSV with FNRs only:
```csv
fnr
123456a
234567b
345678c
```

CSV with company names only:
```csv
name
Example Company GmbH
Another Company AG
Test Industries KG
```

CSV with both (FNR is preferred when both are present):
```csv
fnr,name
123456a,Example Company GmbH
234567b,Another Company AG
345678c,Test Industries KG
```

**Usage:**
```bash
# Basic import
cd backend
python -m services.ingest.bulk_upload --csv path/to/companies.csv

# With custom rate limiting (3 requests per second)
python -m services.ingest.bulk_upload --csv companies.csv --rate-limit 0.33

# With verbose logging
python -m services.ingest.bulk_upload --csv companies.csv --verbose

# With progress updates every 5 companies
python -m services.ingest.bulk_upload --csv companies.csv --progress-interval 5
```

### 2. Import from FNR Range

Iterate through a range of FNR numbers. **Warning:** This will have many misses since FNRs are not sequential.

**Usage:**
```bash
# Import companies from FNR 100000a through 100100z
python -m services.ingest.bulk_upload --range 100000a 100100z

# With custom rate limiting
python -m services.ingest.bulk_upload --range 100000a 100100z --rate-limit 1.0
```

### 3. Single Company Import

Fetch a single company by FNR.

**Usage:**
```bash
# Fetch one company
python -m services.ingest.bulk_upload --fnr 123456a
```

## Command-Line Options

- `--csv PATH` - Path to CSV file containing FNRs or company names
- `--range START_FNR END_FNR` - FNR range to iterate through (e.g., 100000a 200000z)
- `--fnr FNR` - Single FNR to fetch
- `--rate-limit SECONDS` - Minimum seconds between API requests (default: 0.5)
- `--progress-interval N` - Print progress every N companies (default: 10)
- `--verbose` - Enable verbose debug logging

## Rate Limiting

To avoid overwhelming the Firmenbuch API:

- Default: 0.5 seconds between requests (2 requests/second)
- For faster imports: `--rate-limit 0.2` (5 requests/second)
- For slower/safer imports: `--rate-limit 1.0` (1 request/second)

**Note:** Check Firmenbuch API terms of service for rate limiting requirements.

## Statistics and Progress

The script tracks and displays:
- Total companies processed
- Successful fetches
- Failed fetches
- Companies not found
- Skipped entries (invalid format)
- Processing rate (companies/second)
- Time elapsed

Example output:
```
Progress: 100 total | 85 success | 5 failed | 8 not found | 2 skipped | 2.5/sec
============================================================
BULK UPLOAD SUMMARY
============================================================
Total processed: 100
Successful: 85
Failed: 5
Not found: 8
Skipped: 2
Time elapsed: 40.23 seconds
Average rate: 2.49 companies/sec
============================================================
```

## Error Handling

The script handles:
- **Not found** - Company doesn't exist in Firmenbuch (logged, not counted as failure)
- **API errors** - Network issues, SOAP faults (logged, counted as failure, continues)
- **Invalid format** - Malformed FNRs or CSV rows (skipped)
- **Unexpected errors** - Other exceptions (logged, counted as failure, continues)

The script never crashes on a single company error - it logs and continues.

## Example Workflows

### Importing 1000 Companies from CSV

```bash
# 1. Prepare CSV file with FNRs
cat > companies.csv << EOF
fnr
123456a
234567b
345678c
...
EOF

# 2. Run import with progress updates every 50 companies
python -m services.ingest.bulk_upload \\
    --csv companies.csv \\
    --rate-limit 0.5 \\
    --progress-interval 50 \\
    --verbose
```

### Importing by Company Names

```bash
# 1. Prepare CSV with company names
cat > company_names.csv << EOF
name
Österreichische Post AG
OMV Aktiengesellschaft
Erste Group Bank AG
EOF

# 2. Run import
python -m services.ingest.bulk_upload --csv company_names.csv
```

### Testing with Single Company

```bash
# Fetch one company to test configuration
python -m services.ingest.bulk_upload --fnr 123456a --verbose
```

## Environment Setup

Ensure these environment variables are configured in `.env`:

```env
# Supabase credentials
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Firmenbuch API credentials
WSDL_URL=https://justizonline.gv.at/jop/api/at.gv.justiz.fbw/ws?wsdl
API_KEY=your_firmenbuch_api_key
```

## Data Storage

Companies are stored in Supabase with:
- **companies** table - Main company data (fnr, name, legal_form, state)
- **company_addresses** table - Company addresses
- **company_officers** table - Company officers/directors
- **company_activities** table - Business activities

Duplicate prevention:
- Companies are upserted by FNR (existing records are updated)
- Related records (addresses, officers, activities) are replaced on each fetch
- `last_fetched_at` timestamp tracks when data was last updated

## Performance Tips

1. **Use CSV import** - More efficient than FNR range iteration
2. **Adjust rate limiting** - Balance speed vs. API limits
3. **Run during off-hours** - Less API load, faster responses
4. **Batch imports** - Split large datasets into multiple CSV files
5. **Monitor progress** - Use `--progress-interval` to track status
6. **Check logs** - Use `--verbose` to debug issues

## Troubleshooting

### Script fails immediately
- Check environment variables are set (`.env` file)
- Verify Firmenbuch API credentials
- Test Supabase connection

### Many "not found" errors
- FNRs might be incorrect
- Companies might not exist in Firmenbuch
- Try searching by name instead

### API rate limiting errors
- Increase `--rate-limit` value
- Check Firmenbuch API terms for limits
- Consider running during off-peak hours

### Slow performance
- Decrease `--rate-limit` (if allowed by API)
- Check network connection
- Verify Supabase performance

## API Client Functions

For programmatic use, import these functions:

```python
from backend.services.ingest.api_fetch import (
    fetch_company_profile_if_missing,  # Fetch by FNR
    fetch_company_profile_by_name_if_missing,  # Fetch by name
    fetch_company_suggestions_from_firmenbuch,  # Search suggestions
)

# Fetch single company
company = fetch_company_profile_if_missing("123456a")

# Search by name
company = fetch_company_profile_by_name_if_missing("Example GmbH")

# Get suggestions
suggestions = fetch_company_suggestions_from_firmenbuch("Example", limit=10)
```

## Support

For issues or questions:
1. Check logs with `--verbose` flag
2. Review Firmenbuch API documentation
3. Verify database schema and permissions
4. Check network connectivity to API and Supabase
