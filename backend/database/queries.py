"""Database queries for companies."""
from typing import Optional, List
from database.client import get_supabase_client
from supabase import Client


def get_all_companies(limit: int = 100, offset: int = 0) -> List[dict]:
    """Get all companies with pagination."""
    client = get_supabase_client()
    response = client.table('companies').select('*').range(offset, offset + limit - 1).execute()
    return response.data


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


def search_companies(query: str, limit: int = 50) -> List[dict]:
    """Search companies by name or FNR."""
    client = get_supabase_client()
    # Search in both name and fnr fields using case-insensitive matching
    response = client.table('companies').select('*').or_(
        f'name.ilike.%{query}%,fnr.ilike.%{query}%'
    ).limit(limit).execute()
    return response.data


def get_company_with_details(company_id: int) -> Optional[dict]:
    """Get a company with its officers and addresses."""
    client = get_supabase_client()
    
    # Get the company
    company = get_company_by_id(company_id)
    if not company:
        return None
    
    # Get officers
    officers_response = client.table('company_officers').select('*').eq('company_id', company_id).execute()
    
    # Get addresses
    addresses_response = client.table('company_addresses').select('*').eq('company_id', company_id).execute()
    
    # Combine the data
    company['officers'] = officers_response.data or []
    company['addresses'] = addresses_response.data or []
    
    return company


def health_check(db: Client) -> bool:
    """Check if database connection is healthy."""
    try:
        # Try a simple query
        db.table("companies").select("id").limit(1).execute()
        return True
    except Exception:
        return False