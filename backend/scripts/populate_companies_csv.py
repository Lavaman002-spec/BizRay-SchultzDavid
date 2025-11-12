"""
Script to populate Supabase companies table from companies.csv
"""
import csv
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.client import get_supabase_client
from shared.models import CompanyCreate


def normalize_fnr(fnr: str) -> str:
    """Normalize FN number format."""
    if not fnr:
        return ""
    # Remove any whitespace
    fnr = fnr.strip()
    return fnr


def normalize_status(status: str) -> str:
    """Normalize status field."""
    if not status or status.strip() == "":
        return "active"
    
    status = status.strip().lower()
    
    # Map German statuses to English
    status_mapping = {
        "gelöscht": "deleted",
        "aktiv": "active",
        "in liquidation": "liquidation",
        "in liqu.": "liquidation",
    }
    
    for key, value in status_mapping.items():
        if key in status:
            return value
    
    return status if status else "active"


def clean_company_name(name: str) -> str:
    """Clean up company name."""
    if not name:
        return ""
    
    # Remove extra quotes
    name = name.strip().strip('"').strip()
    
    # Remove leading/trailing whitespace
    name = " ".join(name.split())
    
    return name


def read_csv_companies(csv_path: str):
    """Read companies from CSV file."""
    companies = []
    
    print(f"📂 Reading CSV file: {csv_path}")
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
            try:
                fnr = normalize_fnr(row.get('FNR', ''))
                name = clean_company_name(row.get('NAME', ''))
                status = normalize_status(row.get('STATUS', ''))
                legal_form = row.get('RECHTSFORM_TEXT', '').strip()
                
                if not fnr or not name:
                    print(f"⚠️  Row {row_num}: Skipping - missing FNR or NAME")
                    continue
                
                company = {
                    'fnr': fnr,
                    'name': name,
                    'legal_form': legal_form if legal_form else None,
                    'state': status
                }
                
                companies.append(company)
                
            except Exception as e:
                print(f"❌ Error processing row {row_num}: {e}")
                continue
    
    print(f"✅ Successfully parsed {len(companies)} companies from CSV")
    return companies


def insert_companies_batch(supabase, companies, batch_size=100, use_upsert=True):
    """Insert companies in batches with upsert support."""
    total = len(companies)
    inserted = 0
    updated = 0
    errors = 0
    
    operation = "upsert" if use_upsert else "insert"
    print(f"\n🚀 Starting batch {operation} ({batch_size} records per batch)...")
    
    for i in range(0, total, batch_size):
        batch = companies[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        try:
            print(f"   Batch {batch_num}/{total_batches}: Processing {len(batch)} companies...", end=" ")
            
            if use_upsert:
                # Upsert: insert new records or update existing ones based on fnr
                response = supabase.table('companies').upsert(
                    batch,
                    on_conflict='fnr'
                ).execute()
            else:
                # Regular insert
                response = supabase.table('companies').insert(batch).execute()
            
            if response.data:
                # Count as inserted (could be insert or update)
                inserted += len(batch)
                print(f"✅ Success ({inserted}/{total})")
            else:
                errors += len(batch)
                print(f"❌ Failed")
                
        except Exception as e:
            errors += len(batch)
            error_msg = str(e)[:100]
            print(f"❌ Error: {error_msg}")
            continue
    
    return inserted, errors


def main():
    """Main function to populate database."""
    print("=" * 70)
    print("📊 Supabase Company Data Import Script")
    print("=" * 70)
    
    # Get CSV path
    csv_path = Path(__file__).parent.parent / "data" / "companies.csv"
    
    if not csv_path.exists():
        print(f"❌ Error: CSV file not found at {csv_path}")
        return
    
    # Connect to Supabase
    try:
        print("\n🔌 Connecting to Supabase...")
        supabase = get_supabase_client()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return
    
    # Read companies from CSV
    companies = read_csv_companies(str(csv_path))
    
    if not companies:
        print("❌ No companies to insert")
        return
    
    # Choose operation mode
    print(f"\n📋 Found {len(companies)} companies to process")
    print("\nOperation modes:")
    print("  1. UPSERT - Insert new or update existing (recommended)")
    print("  2. INSERT - Only insert new records (fails on duplicates)")
    
    mode = input("\nSelect mode (1 or 2, default=1): ").strip()
    use_upsert = mode != "2"
    
    operation = "upsert" if use_upsert else "insert"
    response = input(f"\n   Continue with {operation}? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Aborted by user")
        return
    
    # Insert companies
    inserted, errors = insert_companies_batch(supabase, companies, use_upsert=use_upsert)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Import Summary")
    print("=" * 70)
    print(f"✅ Successfully processed: {inserted} companies")
    print(f"❌ Errors: {errors}")
    print(f"📈 Success rate: {(inserted / len(companies) * 100):.1f}%")
    print("=" * 70)
    
    if use_upsert:
        print("\nℹ️  Note: Upsert mode was used - existing records were updated")
    print()


if __name__ == "__main__":
    main()
