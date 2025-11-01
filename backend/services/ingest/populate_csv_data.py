#!/usr/bin/env python3
"""
Populate CSV files with real company data from Austrian Business Register

This script fetches companies from the API and saves them to CSV files
in backend/data/ so users have ~1000 companies available on app startup.
"""

import sys
import os
import csv
import time

# Add ETL directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'etl'))

from etl.bulk_api_ingest import bulk_search_companies, bulk_ingest_from_api
from etl.db import get_connection


def export_staging_to_csv(data_dir: str):
    """Export staging tables to CSV files."""
    
    print("\n" + "=" * 80)
    print("📤 EXPORTING STAGING DATA TO CSV")
    print("=" * 80)
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Export companies
    companies_path = os.path.join(data_dir, "companies.csv")
    print(f"\n→ Exporting companies to {companies_path}")
    
    cur.execute("""
        SELECT register_id, name, city, status
        FROM stg_companies
        ORDER BY register_id
    """)
    rows = cur.fetchall()
    
    with open(companies_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['register_id', 'name', 'city', 'status'])
        writer.writerows(rows)
    
    print(f"  ✓ Exported {len(rows)} companies")
    
    # Export officers
    officers_path = os.path.join(data_dir, "officers.csv")
    print(f"\n→ Exporting officers to {officers_path}")
    
    cur.execute("""
        SELECT company_register_id, person_name, role
        FROM stg_officers
        ORDER BY company_register_id
    """)
    rows = cur.fetchall()
    
    with open(officers_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['company_register_id', 'person_name', 'role'])
        writer.writerows(rows)
    
    print(f"  ✓ Exported {len(rows)} officers")
    
    # Export links
    links_path = os.path.join(data_dir, "links.csv")
    print(f"\n→ Exporting links to {links_path}")
    
    cur.execute("""
        SELECT from_register_id, to_register_id, link_type
        FROM stg_links
        ORDER BY from_register_id
    """)
    rows = cur.fetchall()
    
    with open(links_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['from_register_id', 'to_register_id', 'link_type'])
        writer.writerows(rows)
    
    print(f"  ✓ Exported {len(rows)} links")
    
    cur.close()
    conn.close()
    
    print("\n✓ CSV export complete!")


def main():
    print("=" * 80)
    print("🏭 BULK DATA POPULATION FOR CSV FILES")
    print("=" * 80)
    print()
    print("This script will:")
    print("  1. Fetch ~1000 companies from Austrian Business Register")
    print("  2. Store them in the staging database")
    print("  3. Export to CSV files in backend/data/")
    print("  4. These CSVs will be loaded on app startup")
    print()
    
    # Determine data directory
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    data_dir = os.path.abspath(data_dir)
    
    print(f"📂 Data directory: {data_dir}")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"  ✓ Created directory")
    
    # Step 1: Bulk ingest from API
    print("\n" + "=" * 80)
    print("📥 STEP 1: FETCHING COMPANIES FROM API")
    print("=" * 80)
    
    try:
        from etl.normalize import run_normalization
        
        # Fetch 1000 companies (this will take ~15-30 minutes)
        print("\n⚠️  This will take 15-30 minutes to fetch 1000 companies...")
        print("Press Ctrl+C to cancel\n")
        
        time.sleep(3)  # Give user time to cancel
        
        result = bulk_ingest_from_api(
            max_companies=1000,
            delay_between_requests=0.5,
            use_discovery=True
        )
        
        print(f"\n✓ Fetched {result['success_count']}/{result['total_companies']} companies")
        
        # Step 2: Run normalization
        print("\n" + "=" * 80)
        print("🔄 STEP 2: NORMALIZING DATA")
        print("=" * 80)
        
        run_normalization()
        
        # Step 3: Export to CSV
        export_staging_to_csv(data_dir)
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS!")
        print("=" * 80)
        print(f"\nCSV files are ready in: {data_dir}")
        print("\nThese files will be automatically loaded when users start the app.")
        print("Companies will be immediately available for search.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("You can run this script again to continue populating data.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
