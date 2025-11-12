import csv
import os
from supabase import create_client, Client
from ..shared.config import SUPABASE_URL, SUPABASE_KEY
from ..shared.utils import normalize_fn_number, format_company_name, sanitize_input
from ..shared.models import CompanyCreate

# --- Supabase client ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "companies"

# --- CSV path (relative to this script) ---
CSV_PATH = os.path.join(os.path.dirname(__file__), "../shared/companies.csv")

# --- Read CSV file ---
def read_csv_data(csv_path: str):
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [row for row in reader]
    return rows

# --- Upload data in batches ---
def batch_insert(data, batch_size=500):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        print(f"Inserting batch {i//batch_size + 1} ({len(batch)} records)...")
        response = supabase.table(TABLE_NAME).insert(batch).execute()
        if response.error:
            print(f"❌ Error in batch {i//batch_size + 1}: {response.error}")
        else:
            print(f"✅ Inserted {len(batch)} records successfully.")

# --- Main ---
def main():
    print(f"📂 Loading data from {CSV_PATH}")
    rows = read_csv_data(CSV_PATH)
    print(f"Loaded {len(rows)} rows.")

    companies_to_insert = []
    for row in rows:
        try:
            fnr = normalize_fn_number(row.get("fnr", ""))
            name = format_company_name(row.get("name", ""))
            legal_form = sanitize_input(row.get("legal_form", ""))
            state = sanitize_input(row.get("state", ""))

            company = CompanyCreate(
                fnr=fnr,
                name=name,
                legal_form=legal_form or None,
                state=state or None
            )
            companies_to_insert.append(company.model_dump())
        except Exception as e:
            print(f"⚠️ Skipping row due to error: {e}")

    print(f"Prepared {len(companies_to_insert)} valid records for insertion.")
    batch_insert(companies_to_insert)

if __name__ == "__main__":
    main()
