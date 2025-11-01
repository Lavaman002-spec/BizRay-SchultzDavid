import os
import csv
from .db import get_connection


def ingest_bulk_files():
    """Ingest local CSV data from backend/data/ into the database if available."""
    
    # Try multiple possible locations for data files
    possible_data_dirs = [
        os.path.join(os.path.dirname(__file__), "../../../data"),        # backend/data/
        "/bizray/backend/data",  # Docker path
        os.path.join(os.path.dirname(__file__), "../../../data/bulk"),  # data/bulk/ (fallback)
        "/app/data",       # Docker path (fallback)
    ]
    
    data_dir = None
    for dir_path in possible_data_dirs:
        if os.path.exists(dir_path):
            data_dir = dir_path
            print(f"✓ Found bulk data directory: {data_dir}")
            break
    
    if not data_dir:
        print(f"⚠️ Bulk data directory not found in any of these locations:")
        for path in possible_data_dirs:
            print(f"   - {path}")
        return

    files = ["companies.csv", "officers.csv", "links.csv"]
    conn = get_connection()
    cur = conn.cursor()
    
    ingested_any = False

    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            print(f"⚠️ Skipping missing bulk file: {file_name}")
            continue

        print(f"→ Ingesting {file_name}")
        row_count = 0
        
        with open(file_path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if file_name == "companies.csv":
                        cur.execute("""
                            INSERT INTO stg_companies (register_id, name, city, status, src)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (row.get("register_id"), row.get("name"), row.get("city"), row.get("status"), "CSV"))
                        row_count += 1

                    elif file_name == "officers.csv":
                        cur.execute("""
                            INSERT INTO stg_officers (company_register_id, person_name, role, src)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (row.get("company_register_id"), row.get("person_name"), row.get("role"), "CSV"))
                        row_count += 1

                    elif file_name == "links.csv":
                        cur.execute("""
                            INSERT INTO stg_links (from_register_id, to_register_id, link_type, src)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (row.get("from_register_id"), row.get("to_register_id"), row.get("link_type"), "CSV"))
                        row_count += 1

                except Exception as e:
                    print(f"⚠️ Error inserting row in {file_name}: {e}")

        if row_count > 0:
            print(f"  ✓ Ingested {row_count} rows from {file_name}")
            ingested_any = True

    conn.commit()
    cur.close()
    conn.close()
    
    if ingested_any:
        print("✓ Bulk ingestion complete.")
    else:
        print("⚠️ No bulk data was ingested.")
