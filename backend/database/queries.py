from typing import Optional, List
from database.client import get_supabase_client
from supabase import Client

def get_all_companies(limit: int = 100, offset: int = 0) -> List[dict]:
    """Get all companies with pagination. Includes primary address for each company."""
    client = get_supabase_client()
    response = client.table('companies').select('*').range(offset, offset + limit - 1).execute()
    companies = response.data

    if not companies:
        return []

    # Fetch all addresses in one query - more efficient than looping
    company_ids = [c['id'] for c in companies]
    addresses_response = client.table('company_addresses').select('*').in_(
        'company_id', company_ids
    ).eq('is_active', True).execute()

    # Create a map of company_id to address (first address for each company)
    address_map = {}
    for addr in addresses_response.data:
        company_id = addr['company_id']
        if company_id not in address_map:
            address_map[company_id] = addr

    officers_response = client.table('company_officers').select('*').in_('company_id', company_ids).execute()
    
    officers_map = {}
    for officer in officers_response.data:
        company_id = officer['company_id']
        if company_id not in officers_map:
            officers_map[company_id] = []
        officers_map[company_id].append(officer)


    activities_response = client.table('company_activities').select('*').in_('company_id', company_ids).execute()
    
    activity_map = {}
    for activity in activities_response.data:
        company_id = activity['company_id']
        if company_id not in activity_map:
            activity_map[company_id] = []
        activity_map[company_id].append(activity)

    # Attach everything to companies
    for company in companies:
        company_id = company['id']
        company['address'] = address_map.get(company_id)
        company['officers'] = officers_map.get(company_id, [])
        company['activities'] = activity_map.get(company_id, [])

        # Get *all* active addresses for the 'addresses' array
        all_addresses = [addr for addr in addresses_response.data if addr['company_id'] == company_id]
        company['addresses'] = all_addresses
        
        # And keep the single 'address' field for the basic 'Company' type
        company['address'] = address_map.get(company_id)

    return companies


def get_company_by_id(company_id: int) -> Optional[dict]:
    """Get a company by ID."""
    client = get_supabase_client()
    response = client.table('companies').select('*').eq('id', company_id).execute()
    return response.data[0] if response.data else None


def get_company_by_fnr(fnr: str) -> Optional[dict]:
    """Get a company by Firmenbuch number."""
    client = get_supabase_client()
    response = client.table('companies').select('*').eq('fnr', fnr).execute()
    return response.data[0] if response.data else None


def create_company(company_data: dict) -> dict:
    """Create a new company."""
    client = get_supabase_client()
    response = client.table('companies').insert(company_data).execute()
    return response.data[0] if response.data else None


def update_company(company_id: int, company_data: dict) -> Optional[dict]:
    """Update a company."""
    client = get_supabase_client()
    response = client.table('companies').update(company_data).eq('id', company_id).execute()
    return response.data[0] if response.data else None


def delete_company(company_id: int) -> bool:
    """Delete a company."""
    client = get_supabase_client()
    response = client.table('companies').delete().eq('id', company_id).execute()
    return True


def search_companies(query: str, limit: int = 50, city: Optional[str] = None) -> List[dict]:
    """Search companies by name or FNR, optionally filtered by city.
    Returns companies with their primary address."""
    client = get_supabase_client()

    if city:
        # When filtering by city, we need to join with company_addresses
        # First get company IDs that match the city
        addresses_response = client.table('company_addresses').select('company_id').ilike('city', city).execute()
        company_ids = [addr['company_id'] for addr in addresses_response.data if addr.get('company_id')]

        if not company_ids:
            # No companies found in that city
            return []

        # Search in both name and fnr fields, filtered by company IDs
        response = client.table('companies').select('*').or_(
            f'name.ilike.%{query}%,fnr.ilike.%{query}%'
        ).in_('id', company_ids).limit(limit).execute()
    else:
        # Search in both name and fnr fields using case-insensitive matching
        response = client.table('companies').select('*').or_(
            f'name.ilike.%{query}%,fnr.ilike.%{query}%'
        ).limit(limit).execute()

    companies = response.data

    if not companies:
        return []

    # Fetch all addresses in one query - more efficient than looping
    company_ids = [c['id'] for c in companies]
    addresses_response = client.table('company_addresses').select('*').in_(
        'company_id', company_ids
    ).eq('is_active', True).execute()

    # Create a map of company_id to address (first address for each company)
    address_map = {}
    for addr in addresses_response.data:
        company_id = addr['company_id']
        if company_id not in address_map:
            address_map[company_id] = addr

    # Attach addresses to companies
    for company in companies:
        company['address'] = address_map.get(company['id'])

    return companies


def get_company_with_details(company_id: int) -> Optional[dict]:
    """Get a company with its officers, addresses, and activities."""
    client = get_supabase_client()
    
    # Get the company
    company = get_company_by_id(company_id)
    if not company:
        return None
    
    # Get officers
    officers_response = client.table('company_officers').select('*').eq('company_id', company_id).execute()
    
    # Get addresses
    addresses_response = client.table('company_addresses').select('*').eq('company_id', company_id).execute()
    
    # Get activities
    activities_response = client.table('company_activities').select('*').eq('company_id', company_id).execute()

    # Combine the data
    company['officers'] = officers_response.data or []
    company['addresses'] = addresses_response.data or []
    company['activities'] = activities_response.data or [] # <-- ADD THIS LINE
    
    return company


def get_unique_cities() -> List[str]:
    """Get all unique cities from company_addresses table."""
    client = get_supabase_client()

    # Get all unique cities
    response = client.table('company_addresses').select('city').execute()

    # Extract unique cities and filter out nulls/empty strings
    cities = set()
    for row in response.data:
        city = row.get('city')
        if city and city.strip():
            cities.add(city.strip())

    # Return sorted list
    return sorted(list(cities))


def get_company_name_suggestions(query: str, limit: int = 10) -> List[str]:
    """Get company name suggestions for autocomplete based on partial query."""
    client = get_supabase_client()

    # Search for company names that match the query
    response = client.table('companies').select('name').ilike(
        'name', f'%{query}%'
    ).limit(limit).execute()

    # Extract unique company names
    suggestions = []
    seen = set()
    for row in response.data:
        name = row.get('name')
        if name and name not in seen:
            suggestions.append(name)
            seen.add(name)

    return suggestions


def health_check(db: Client) -> bool:
    """Check if database connection is healthy."""
    try:
        # Try a simple query
        db.table("companies").select("id").limit(1).execute()
        return True
    except Exception:
        return False