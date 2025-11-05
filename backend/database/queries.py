"""Database queries for companies."""
from typing import Optional, List, Tuple, Dict

from database.client import get_supabase_client
from supabase import Client
from shared.models import SearchQuery


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


def _attach_company_relations(
    companies: List[dict], client: Client
) -> List[dict]:
    """Attach related officers and addresses to company records."""

    if not companies:
        return []

    company_ids = [company.get("id") for company in companies if company.get("id") is not None]
    if not company_ids:
        return companies

    officers_response = (
        client.table("company_officers")
        .select("*")
        .in_("company_id", company_ids)
        .execute()
    )
    addresses_response = (
        client.table("company_addresses")
        .select("*")
        .in_("company_id", company_ids)
        .execute()
    )

    officers_by_company: Dict[int, List[dict]] = {company_id: [] for company_id in company_ids}
    for officer in officers_response.data or []:
        company_id = officer.get("company_id")
        if company_id in officers_by_company:
            officers_by_company[company_id].append(officer)

    addresses_by_company: Dict[int, List[dict]] = {company_id: [] for company_id in company_ids}
    for address in addresses_response.data or []:
        company_id = address.get("company_id")
        if company_id in addresses_by_company:
            addresses_by_company[company_id].append(address)

    for company in companies:
        company_id = company.get("id")
        if company_id is None:
            continue
        company["officers"] = officers_by_company.get(company_id, [])
        company["addresses"] = addresses_by_company.get(company_id, [])

    return companies


def search_companies(query: str, limit: int = 50, offset: int = 0) -> Tuple[List[dict], int]:
    """Search companies by name or FNR with pagination."""

    client = get_supabase_client()
    response = (
        client.table("companies")
        .select("*", count="exact")
        .or_(f"name.ilike.%{query}%,fnr.ilike.%{query}%")
        .range(offset, offset + limit - 1)
        .execute()
    )

    companies = response.data or []
    for company in companies:
        company.setdefault("officers", [])
        company.setdefault("addresses", [])

    total = response.count or 0
    return companies, total


def search_companies_advanced(search: SearchQuery) -> Tuple[List[dict], int]:
    """Perform an advanced search using the structured search query."""

    client = get_supabase_client()

    pagination = search.pagination
    limit = pagination.limit
    offset = pagination.offset

    query_builder = client.table("companies").select("*", count="exact")

    term = search.q.strip()
    if term:
        pattern = f"%{term}%"
        query_builder = query_builder.or_(
            f"name.ilike.{pattern},fnr.ilike.{pattern}"
        )

    filters = search.filters
    if filters:
        if filters.legal_forms:
            query_builder = query_builder.in_("legal_form", filters.legal_forms)
        if filters.states:
            query_builder = query_builder.in_("state", filters.states)
        if filters.cities:
            query_builder = query_builder.in_("city", filters.cities)

    if search.sort:
        query_builder = query_builder.order(
            search.sort.field, desc=search.sort.direction == "desc"
        )
    else:
        query_builder = query_builder.order("name", desc=False)

    response = query_builder.range(offset, offset + limit - 1).execute()

    companies = response.data or []
    for company in companies:
        company.setdefault("officers", [])
        company.setdefault("addresses", [])

    if search.include_relations:
        companies = _attach_company_relations(companies, client)

    total = response.count or len(companies)
    return companies, total


def search_companies_with_relations(search: SearchQuery) -> Tuple[List[dict], int]:
    """Perform an advanced search and include related officers and addresses."""

    return search_companies_advanced(search.model_copy(update={"include_relations": True}))


def get_search_suggestions(query: str, limit: int = 10) -> List[dict]:
    """Return autocomplete suggestions for the provided query."""

    client = get_supabase_client()
    term = query.strip()
    if not term:
        return []

    pattern = f"{term}%"
    response = (
        client.table("companies")
        .select("name, fnr")
        .ilike("name", pattern)
        .order("name")
        .limit(limit)
        .execute()
    )

    return response.data or []


def get_search_stats() -> dict:
    """Return high-level search statistics."""

    client = get_supabase_client()
    response = client.table("companies").select("id", count="exact").limit(1).execute()
    total_companies = response.count or 0
    return {"total_companies": total_companies}


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