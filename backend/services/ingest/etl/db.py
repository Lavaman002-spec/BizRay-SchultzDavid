import os
import psycopg2
from .config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def ensure_schema():
    conn = get_connection()
    cur = conn.cursor()
    
    # Find the migration file - try multiple paths
    migration_paths = [
        "/app/db/migrations/001_init.sql",  # Docker path
        os.path.join(os.path.dirname(__file__), "../../../db/migrations/001_init.sql"),  # Relative path
        "../../db/migrations/001_init.sql",  # Alternative relative
    ]
    
    migration_file = None
    for path in migration_paths:
        if os.path.exists(path):
            migration_file = path
            break
    
    if not migration_file:
        print("⚠️ Warning: Could not find migration file. Trying to continue...")
        return
    
    print(f"→ Applying migration from {migration_file}")

    with open(migration_file, "r") as f:
        sql = f.read()
        cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()
    print("✓ Schema ensured / already exists.")