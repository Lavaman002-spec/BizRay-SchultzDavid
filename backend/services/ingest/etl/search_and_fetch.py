"""
Search and Fetch Module

Searches for companies locally and fetches from API if not found.
"""

import sys
import os
from typing import Dict, List, Optional
import importlib.util
from zeep.helpers import serialize_object

# Load modules explicitly to avoid import conflicts
current_dir = os.path.dirname(os.path.abspath(__file__))

def load_module(module_name, file_name):
    """Load a module from the current directory explicitly."""
    file_path = os.path.join(current_dir, file_name)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f'etl_{module_name}'] = module  # Use unique name to avoid conflicts
    spec.loader.exec_module(module)
    return module

# Load our modules explicitly
client_module = load_module('client', 'client.py')
api_fetch_module = load_module('api_fetch', 'api_fetch.py')
normalize_module = load_module('normalize', 'normalize.py')
db_module = load_module('db', 'db.py')

create_client = client_module.create_client
fetch_company_data = api_fetch_module.fetch_company
run_normalization = normalize_module.run_normalization
get_connection = db_module.get_connection


def search_api_companies(query: str, max_results: int = 10) -> List[Dict]:
    """
    Search for companies in the Austrian Business Register API by name.
    
    Args:
        query: Company name to search for
        max_results: Maximum number of results to return
        
    Returns:
        List of company info dicts with FNR and FIRMA
    """
    client = create_client()
    
    try:
        # Search by company name
        params = {
            "FIRMENWORTLAUT": query,
            "EXAKTESUCHE": False,  # Partial match
            "SUCHBEREICH": 1,      # Normal search
            "GERICHT": "",
            "RECHTSFORM": "",      # All legal forms
            "RECHTSEIGENSCHAFT": "",
            "ORTNR": ""            # All locations
        }
        
        resp = client.service.SUCHEFIRMA(**params)
        result = serialize_object(resp)
        
        companies = []
        if result and result.get('ERGEBNIS'):
            for company in result['ERGEBNIS'][:max_results]:
                if isinstance(company, dict):
                    fnr = company.get('FNR', '')
                    firma = company.get('FIRMA', '')
                    
                    # Convert FNR format: add space before last character
                    if fnr and ' ' not in fnr and len(fnr) > 1:
                        fnr = fnr[:-1] + ' ' + fnr[-1]
                    
                    companies.append({
                        'fnr': fnr,
                        'firma': firma,
                        'raw': company
                    })
        
        return companies
        
    except Exception as e:
        print(f"API search failed: {e}")
        return []


def search_local_companies(query: str, limit: int = 10) -> List[Dict]:
    """
    Search for companies in the local database.
    
    Args:
        query: Company name or register ID to search for
        limit: Maximum number of results
        
    Returns:
        List of company dicts from database
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        q_like = f"%{query}%"
        
        cur.execute("""
            SELECT id, register_id, name, city, status, legal_form
            FROM companies
            WHERE name ILIKE %s OR register_id ILIKE %s
            ORDER BY name ASC
            LIMIT %s
        """, (q_like, q_like, limit))
        
        rows = cur.fetchall()
        
        companies = []
        for row in rows:
            companies.append({
                'id': str(row[0]),
                'register_id': row[1],
                'name': row[2],
                'city': row[3],
                'status': row[4],
                'legal_form': row[5],
                'source': 'database'
            })
        
        return companies
        
    finally:
        cur.close()
        conn.close()


def search_and_fetch(
    query: str,
    fetch_if_not_found: bool = True,
    max_api_results: int = 5,
    max_to_fetch: int = 1
) -> Dict:
    """
    Search for companies locally, and fetch from API if not found.
    
    This is the main function that implements the "search-and-fetch" pattern:
    1. Search local database first
    2. If no results and fetch_if_not_found=True, search API
    3. Fetch detailed data for found companies
    4. Normalize and return results
    
    Args:
        query: Company name to search for
        fetch_if_not_found: If True, fetch from API when not found locally
        max_api_results: Maximum API search results to consider
        max_to_fetch: Maximum number of companies to fetch from API
        
    Returns:
        Dict with:
            - found_in_database: bool
            - local_results: List of companies from database
            - api_results: List of companies found in API (if searched)
            - fetched: List of companies fetched from API
            - total_results: int
    """
    result = {
        'found_in_database': False,
        'local_results': [],
        'api_results': [],
        'fetched': [],
        'total_results': 0,
        'query': query
    }
    
    print(f"\n🔍 Searching for: '{query}'")
    
    # Step 1: Search local database
    print("  [1/3] Searching local database...")
    local_results = search_local_companies(query, limit=10)
    result['local_results'] = local_results
    
    if local_results:
        result['found_in_database'] = True
        result['total_results'] = len(local_results)
        print(f"  ✓ Found {len(local_results)} companies in database")
        return result
    
    print("  ⚠️  No results in local database")
    
    # Step 2: Search API if not found locally
    if not fetch_if_not_found:
        print("  ⏭️  Skipping API search (fetch_if_not_found=False)")
        return result
    
    print(f"  [2/3] Searching Austrian Business Register API...")
    api_results = search_api_companies(query, max_results=max_api_results)
    result['api_results'] = api_results
    
    if not api_results:
        print("  ⚠️  No results found in API")
        return result
    
    print(f"  ✓ Found {len(api_results)} companies in API")
    
    # Step 3: Fetch detailed data for top results
    print(f"  [3/3] Fetching detailed data for top {max_to_fetch} companies...")
    fetched_companies = []
    
    for i, company in enumerate(api_results[:max_to_fetch]):
        fnr = company['fnr']
        print(f"    → Fetching {fnr} ({company.get('firma', 'Unknown')[:50]})")
        
        try:
            company_data = fetch_company_data(fnr)
            if company_data:
                fetched_companies.append({
                    'fnr': fnr,
                    'name': company_data.get('name'),
                    'city': company_data.get('city'),
                    'legal_form': company_data.get('legal_form'),
                    'status': company_data.get('status')
                })
                print(f"    ✓ Fetched: {company_data.get('name')}")
            else:
                print(f"    ⚠️  Failed to fetch {fnr}")
        except Exception as e:
            print(f"    ❌ Error fetching {fnr}: {e}")
        
        # Rate limiting
        if i < len(api_results[:max_to_fetch]) - 1:
            time.sleep(0.5)
    
    result['fetched'] = fetched_companies
    
    # Step 4: Normalize data
    if fetched_companies:
        print(f"  → Normalizing {len(fetched_companies)} companies...")
        try:
            run_normalization()
            print("  ✓ Normalization complete")
            
            # Re-search local database to get normalized results
            local_results = search_local_companies(query, limit=10)
            result['local_results'] = local_results
            result['found_in_database'] = True
            result['total_results'] = len(local_results) + len(api_results)
        except Exception as e:
            print(f"  ⚠️  Normalization failed: {e}")
    
    print(f"\n📊 Search and Fetch Summary:")
    print(f"   Query: '{query}'")
    print(f"   Found in DB: {len(result['local_results'])}")
    print(f"   Found in API: {len(result['api_results'])}")
    print(f"   Fetched: {len(result['fetched'])}")
    
    return result


def interactive_search_and_fetch():
    """
    Interactive CLI for searching and fetching companies.
    """
    print("=" * 70)
    print("🔍 Interactive Company Search and Fetch")
    print("=" * 70)
    print("\nThis tool searches your local database first.")
    print("If no results found, it searches the Austrian Business Register API")
    print("and fetches detailed company data.\n")
    
    while True:
        query = input("Enter company name to search (or 'q' to quit): ").strip()
        
        if query.lower() == 'q':
            print("\nGoodbye!")
            break
        
        if not query:
            print("⚠️  Please enter a search query")
            continue
        
        # Perform search and fetch
        result = search_and_fetch(
            query=query,
            fetch_if_not_found=True,
            max_api_results=5,
            max_to_fetch=1  # Fetch only the top match
        )
        
        # Display results
        print("\n" + "=" * 70)
        print("📋 Results:")
        print("=" * 70)
        
        if result['local_results']:
            print(f"\n✓ Found {len(result['local_results'])} companies in database:")
            for i, company in enumerate(result['local_results'][:5], 1):
                print(f"  {i}. {company['name']}")
                print(f"     ID: {company['register_id']}, City: {company['city']}")
        
        if result['api_results'] and not result['local_results']:
            print(f"\n📡 Found {len(result['api_results'])} companies in API:")
            for i, company in enumerate(result['api_results'][:5], 1):
                print(f"  {i}. FNR: {company['fnr']}, Name: {company.get('firma', 'N/A')}")
        
        if result['fetched']:
            print(f"\n⬇️  Fetched and stored {len(result['fetched'])} companies")
        
        print("\n" + "=" * 70)
        print()


if __name__ == "__main__":
    # Run interactive mode when executed directly
    interactive_search_and_fetch()
