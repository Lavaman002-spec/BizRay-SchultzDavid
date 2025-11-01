import os
import sys
import time
import psycopg2

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


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