"""
ETL Run Once - Initial Data Loading

This script runs once when the application starts to:
1. Initialize the database schema
2. Load bulk CSV data if available
3. Run normalization

It's designed to be run by the etl_once Docker service.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.db import ensure_schema, wait_for_db
from etl.bulk_ingest import ingest_bulk_files
from etl.normalize import run_normalization


def main():
    print("=" * 80)
    print("🚀 BIZRAY ETL - INITIAL DATA LOADING")
    print("=" * 80)
    
    # Step 1: Wait for database to be ready
    print("\n[1/4] Waiting for database...")
    wait_for_db()
    print("  ✓ Database is ready")
    
    # Step 2: Ensure schema exists
    print("\n[2/4] Ensuring database schema...")
    ensure_schema()
    print("  ✓ Schema initialized")
    
    # Step 3: Load bulk CSV files
    print("\n[3/4] Loading bulk CSV data...")
    try:
        ingest_bulk_files()
    except Exception as e:
        print(f"  ⚠️  Error loading CSV files: {e}")
        print("  → This is OK if CSV files don't exist yet")
    
    # Step 4: Run normalization
    print("\n[4/4] Running normalization...")
    try:
        run_normalization()
    except Exception as e:
        print(f"  ⚠️  Error running normalization: {e}")
        print("  → This is OK if there's no data to normalize yet")
    
    print("\n" + "=" * 80)
    print("✅ ETL INITIALIZATION COMPLETE")
    print("=" * 80)
    print("\nThe application is ready to use!")
    print("Database is initialized and bulk data (if available) has been loaded.")
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
