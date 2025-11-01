import sys
import time
import psycopg2
from .db import ensure_schema, get_connection
from .bulk_ingest import ingest_bulk_files
from .bulk_api_ingest import bulk_ingest_from_api
from .normalize import run_normalization
from .api_fetch import fetch_company
from .config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def wait_for_db(retries=10, delay=3):
    """Wait until PostgreSQL is ready before proceeding."""
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME
            )
            conn.close()
            print("✅ Database is ready!")
            return True
        except psycopg2.OperationalError as e:
            print(f"⏳ Waiting for database... (attempt {attempt + 1}/{retries})")
            if attempt == retries - 1:
                print(f"   Error: {e}")
            time.sleep(delay)
    print("❌ Database not reachable after several attempts.")
    print(f"   Connection details: host={DB_HOST}, port={DB_PORT}, db={DB_NAME}, user={DB_USER}")
    sys.exit(1)


def run_etl(sample_companies=None, use_bulk_api=False, max_bulk_companies=100):
    """
    Run the complete ETL pipeline.
    
    Args:
        sample_companies: List of company register IDs to fetch. 
                         If None, uses default samples.
        use_bulk_api: If True, use bulk API ingestion instead of sample companies
        max_bulk_companies: Maximum number of companies to fetch in bulk mode
    """
    wait_for_db()

    print("=" * 60)
    print("Starting BizRay ETL Pipeline")
    print("=" * 60)

    # Step 1: Ensure database schema exists
    print("\n[1/5] Ensuring database schema...")
    try:
        ensure_schema()
    except Exception as e:
        print(f"⚠️ Schema setup failed: {e}")
        print("   Continuing anyway - schema may already exist")

    # Step 2: Ingest bulk files if available
    print("\n[2/5] Ingesting bulk CSV files (if any)...")
    try:
        ingest_bulk_files()
    except Exception as e:
        print(f"⚠️ Bulk ingestion failed (non-critical): {e}")

    # Step 3: Fetch data from API
    if use_bulk_api:
        print("\n[3/5] Fetching company data from API (BULK MODE)...")
        try:
            stats = bulk_ingest_from_api(
                company_list=sample_companies,
                max_companies=max_bulk_companies,
                delay_between_requests=1.0,
                use_discovery=True
            )
            fetched_count = stats['successful']
            failed_count = stats['failed']
        except Exception as e:
            print(f"❌ Bulk API ingestion failed: {e}")
            fetched_count = 0
            failed_count = 0
    else:
        print("\n[3/5] Fetching company data from API (SAMPLE MODE)...")
        if sample_companies is None:
            sample_companies = [
                "FN348406",
                "FN10001",
                "FN10002",
            ]
        
        fetched_count = 0
        failed_count = 0
        
        for company_id in sample_companies:
            try:
                print(f"\n→ Fetching {company_id}...")
                data = fetch_company(company_id)
                if data:
                    fetched_count += 1
                    print(f"  ✓ Success: {data['name']} ({data['register_id']})")
                else:
                    failed_count += 1
                    print(f"  ⚠️ No data returned for {company_id}")
            except Exception as e:
                failed_count += 1
                print(f"  ❌ Error fetching {company_id}: {e}")
    
    print(f"\nAPI Fetch Summary: {fetched_count} succeeded, {failed_count} failed")

    # Step 4: Normalize and transform data
    print("\n[4/5] Normalizing and transforming data...")
    try:
        run_normalization()
    except Exception as e:
        print(f"❌ Normalization failed: {e}")
        raise

    # Step 5: Verification
    print("\n[5/5] Verifying data...")
    verify_data()

    print("\n" + "=" * 60)
    print("✅ ETL Pipeline Complete!")
    print("=" * 60)


def verify_data():
    """Verify that data was properly loaded into canonical tables."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM companies")
        company_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM officers")
        officer_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM ownership_links")
        link_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM stg_companies")
        stg_company_count = cur.fetchone()[0]
        
        print(f"\nData Verification:")
        print(f"  Canonical Companies: {company_count}")
        print(f"  Canonical Officers: {officer_count}")
        print(f"  Ownership Links: {link_count}")
        print(f"  Staging Companies: {stg_company_count}")
        
        if company_count == 0:
            print("  ⚠️ Warning: No companies in canonical table!")
        
    except Exception as e:
        print(f"⚠️ Verification failed: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    try:
        run_etl()
    except KeyboardInterrupt:
        print("\n⚠️ ETL interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ETL failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
