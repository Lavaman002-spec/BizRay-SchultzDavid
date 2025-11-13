#!/usr/bin/env python3
"""Apply database migration for exports table."""
import sys
from pathlib import Path

# Add backend to path
BACKEND_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.database.client import get_supabase_client

def apply_migration():
    """Apply the exports table migration."""
    client = get_supabase_client()

    # Read the migration file
    migration_file = BACKEND_ROOT / "database" / "migrations" / "add_exports_table.sql"
    with open(migration_file, 'r') as f:
        sql = f.read()

    print("Applying migration: add_exports_table.sql")
    print("=" * 60)

    try:
        # Execute the SQL
        # Note: Supabase's Python client doesn't directly support raw SQL execution
        # We need to use the PostgREST API or execute via the dashboard
        print("⚠️  The Supabase Python client doesn't support raw SQL execution.")
        print("\nPlease apply the migration manually:")
        print("1. Go to: https://ufycggwohzqzabzqjhzm.supabase.co")
        print("2. Navigate to SQL Editor")
        print("3. Run the following SQL:\n")
        print(sql)
        print("\n" + "=" * 60)

        # Alternative: Check if table exists
        try:
            response = client.table('exports').select('id').limit(1).execute()
            print("\n✅ SUCCESS: The 'exports' table already exists!")
            return True
        except Exception as e:
            print(f"\n❌ ERROR: The 'exports' table does not exist yet.")
            print(f"   Details: {str(e)}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
