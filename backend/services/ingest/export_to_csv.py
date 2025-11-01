#!/usr/bin/env python3
"""
Export current database to CSV files

This script exports the current canonical database tables to CSV files
in backend/data/ for bulk loading on app startup.
"""

import sys
import os
import csv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'etl'))

from etl.db import get_connection


def export_to_csv():
    """Export canonical tables to CSV files."""
    
    # Determine data directory
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    data_dir = os.path.abspath(data_dir)
    
    print("=" * 80)
    print("📤 EXPORTING DATABASE TO CSV FILES")
    print("=" * 80)
    print(f"\n📂 Data directory: {data_dir}\n")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"  ✓ Created directory")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Export companies
    companies_path = os.path.join(data_dir, "companies.csv")
    print(f"→ Exporting companies to {companies_path}")
    
    cur.execute("""
        SELECT register_id, name, city, status
        FROM companies
        WHERE register_id IS NOT NULL
        ORDER BY register_id
    """)
    rows = cur.fetchall()
    
    with open(companies_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['register_id', 'name', 'city', 'status'])
        for row in rows:
            writer.writerow([
                row[0] or '',
                row[1] or '',
                row[2] or '',
                row[3] or ''
            ])
    
    print(f"  ✓ Exported {len(rows)} companies")
    
    # Export officers
    officers_path = os.path.join(data_dir, "officers.csv")
    print(f"\n→ Exporting officers to {officers_path}")
    
    cur.execute("""
        SELECT c.register_id, o.person_name, o.role
        FROM officers o
        JOIN companies c ON o.company_id = c.id
        WHERE c.register_id IS NOT NULL
        ORDER BY c.register_id
    """)
    rows = cur.fetchall()
    
    with open(officers_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['company_register_id', 'person_name', 'role'])
        for row in rows:
            writer.writerow([
                row[0] or '',
                row[1] or '',
                row[2] or ''
            ])
    
    print(f"  ✓ Exported {len(rows)} officers")
    
    # Export links
    links_path = os.path.join(data_dir, "links.csv")
    print(f"\n→ Exporting links to {links_path}")
    
    try:
        cur.execute("""
            SELECT c1.register_id, c2.register_id, l.link_type
            FROM links l
            JOIN companies c1 ON l.from_company_id = c1.id
            JOIN companies c2 ON l.to_company_id = c2.id
            WHERE c1.register_id IS NOT NULL AND c2.register_id IS NOT NULL
            ORDER BY c1.register_id
        """)
        rows = cur.fetchall()
    except Exception as e:
        print(f"  ⚠️  Links table doesn't exist or is empty: {e}")
        rows = []
    
    with open(links_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['from_register_id', 'to_register_id', 'link_type'])
        for row in rows:
            writer.writerow([
                row[0] or '',
                row[1] or '',
                row[2] or ''
            ])
    
    print(f"  ✓ Exported {len(rows)} links")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ EXPORT COMPLETE!")
    print("=" * 80)
    print(f"\nCSV files saved to: {data_dir}")
    print("\nThese files will be automatically loaded when the app starts.")
    

if __name__ == "__main__":
    try:
        export_to_csv()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
