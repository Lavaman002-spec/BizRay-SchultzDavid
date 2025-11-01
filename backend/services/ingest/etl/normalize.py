from .db import get_connection
import hashlib


def run_normalization():
    """
    Perform deduplication and transform staging data into canonical tables.
    
    This process:
    1. Deduplicates staging data
    2. Transforms stg_companies → companies with canonical keys
    3. Links stg_officers → officers with proper company FKs
    4. Maps stg_links → ownership_links with company UUIDs
    """
    print("→ Running normalization and transformation...")
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Step 1: Remove duplicates from staging tables
        print("  Step 1: Deduplicating staging data...")
        _deduplicate_staging(cur)
        
        # Step 2: Transform companies from staging to canonical
        print("  Step 2: Transforming companies to canonical...")
        _transform_companies(cur)
        
        # Step 3: Transform officers from staging to canonical
        print("  Step 3: Transforming officers to canonical...")
        _transform_officers(cur)
        
        # Step 4: Transform ownership links
        print("  Step 4: Transforming ownership links...")
        _transform_links(cur)
        
        # Step 5: Clean and normalize text data
        print("  Step 5: Cleaning and normalizing text...")
        _clean_text_data(cur)
        
        conn.commit()
        print("✓ Normalization and transformation complete.")
        
    except Exception as e:
        print(f"⚠️ Normalization failed: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def _deduplicate_staging(cur):
    """Remove duplicates from staging tables based on key fields."""
    
    # Deduplicate stg_companies by register_id (keep most recent)
    cur.execute("""
        DELETE FROM stg_companies a
        USING stg_companies b
        WHERE a.id < b.id 
        AND a.register_id = b.register_id
        AND a.register_id IS NOT NULL;
    """)
    deleted = cur.rowcount
    if deleted > 0:
        print(f"    ✓ Removed {deleted} duplicate companies from staging")
    
    # Deduplicate stg_officers by company + person
    cur.execute("""
        DELETE FROM stg_officers a
        USING stg_officers b
        WHERE a.id < b.id 
        AND a.company_register_id = b.company_register_id
        AND a.person_name = b.person_name
        AND a.role = b.role;
    """)
    deleted = cur.rowcount
    if deleted > 0:
        print(f"    ✓ Removed {deleted} duplicate officers from staging")


def _generate_canonical_key(register_id: str) -> str:
    """
    Generate a canonical key for a company.
    This ensures consistent identification across different data sources.
    """
    # Normalize the register ID (remove prefixes, lowercase, etc.)
    normalized = register_id.strip().upper().replace('FN', '').replace(' ', '')
    # Create a deterministic hash
    return f"AT-{normalized}"


def _transform_companies(cur):
    """
    Transform staging companies into canonical companies table.
    Uses INSERT ... ON CONFLICT to handle duplicates.
    """
    cur.execute("""
        INSERT INTO companies (
            canonical_key,
            register_id,
            name,
            legal_form,
            status,
            address_line,
            city,
            country
        )
        SELECT DISTINCT ON (register_id)
            'AT-' || UPPER(REPLACE(REPLACE(register_id, 'FN', ''), ' ', '')) as canonical_key,
            register_id,
            name,
            legal_form,
            status,
            address_line,
            city,
            COALESCE(country, 'AT') as country
        FROM stg_companies
        WHERE register_id IS NOT NULL
        ON CONFLICT (canonical_key) DO UPDATE SET
            name = EXCLUDED.name,
            legal_form = EXCLUDED.legal_form,
            status = EXCLUDED.status,
            address_line = EXCLUDED.address_line,
            city = EXCLUDED.city,
            country = EXCLUDED.country;
    """)
    
    inserted = cur.rowcount
    print(f"    ✓ Upserted {inserted} companies into canonical table")


def _transform_officers(cur):
    """
    Transform staging officers into canonical officers table.
    Links officers to companies via UUID foreign key.
    """
    cur.execute("""
        INSERT INTO officers (
            company_id,
            person_id,
            person_name,
            role
        )
        SELECT DISTINCT ON (c.id, so.person_name, so.role)
            c.id as company_id,
            so.person_id,
            so.person_name,
            so.role
        FROM stg_officers so
        JOIN companies c ON c.register_id = so.company_register_id
        WHERE so.person_name IS NOT NULL
        ON CONFLICT DO NOTHING;
    """)
    
    inserted = cur.rowcount
    print(f"    ✓ Inserted {inserted} officers into canonical table")


def _transform_links(cur):
    """
    Transform staging ownership links into canonical ownership_links table.
    Resolves register IDs to company UUIDs.
    """
    cur.execute("""
        INSERT INTO ownership_links (
            from_company_id,
            to_company_id,
            link_type
        )
        SELECT DISTINCT ON (c1.id, c2.id, sl.link_type)
            c1.id as from_company_id,
            c2.id as to_company_id,
            sl.link_type
        FROM stg_links sl
        JOIN companies c1 ON c1.register_id = sl.from_register_id
        JOIN companies c2 ON c2.register_id = sl.to_register_id
        WHERE sl.from_register_id IS NOT NULL 
        AND sl.to_register_id IS NOT NULL
        ON CONFLICT DO NOTHING;
    """)
    
    inserted = cur.rowcount
    print(f"    ✓ Inserted {inserted} ownership links into canonical table")


def _clean_text_data(cur):
    """
    Clean and normalize text data in canonical tables.
    - Trim whitespace
    - Normalize casing for city names
    - Handle NULL values
    """
    # Clean company names and addresses
    cur.execute("""
        UPDATE companies
        SET 
            name = TRIM(name),
            city = INITCAP(TRIM(city)),
            address_line = TRIM(address_line)
        WHERE name IS NOT NULL;
    """)
    
    # Clean officer names
    cur.execute("""
        UPDATE officers
        SET person_name = TRIM(person_name)
        WHERE person_name IS NOT NULL;
    """)
    
    print(f"    ✓ Cleaned text data in canonical tables")


def clear_staging_tables():
    """
    Clear all staging tables after successful transformation.
    Use this after verifying canonical data is correct.
    """
    print("→ Clearing staging tables...")
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("TRUNCATE stg_companies, stg_officers, stg_links CASCADE;")
        conn.commit()
        print("✓ Staging tables cleared.")
    except Exception as e:
        print(f"⚠️ Failed to clear staging: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()