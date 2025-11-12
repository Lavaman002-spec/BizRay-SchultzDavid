"""Script to inspect current Supabase database schema."""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from ..database.client import get_supabase_client


def inspect_database():
    """Inspect and display current database schema."""
    client = get_supabase_client()
    
    print("🔍 Inspecting Supabase Database Schema...\n")
    
    # Check companies table
    print("📊 COMPANIES TABLE:")
    try:
        result = client.table('companies').select('*').limit(1).execute()
        if result.data:
            print(f"   Columns: {', '.join(result.data[0].keys())}")
            print(f"   Sample row: {result.data[0]}")
        else:
            print("   ⚠️  Table is empty")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n👥 COMPANY_OFFICERS TABLE:")
    try:
        result = client.table('company_officers').select('*').limit(1).execute()
        if result.data:
            print(f"   Columns: {', '.join(result.data[0].keys())}")
            print(f"   Sample row: {result.data[0]}")
        else:
            print("   ⚠️  Table is empty")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🔗 LINKS TABLE:")
    try:
        result = client.table('links').select('*').limit(1).execute()
        if result.data:
            print(f"   Columns: {', '.join(result.data[0].keys())}")
        else:
            print("   ⚠️  Table exists but is empty")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n📍 COMPANY_ADDRESSES TABLE:")
    try:
        result = client.table('company_addresses').select('*').limit(1).execute()
        if result.data:
            print(f"   Columns: {', '.join(result.data[0].keys())}")
        else:
            print("   ⚠️  Table exists but is empty")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    inspect_database()