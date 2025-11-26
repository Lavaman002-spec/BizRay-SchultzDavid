"""Database queries for companies."""
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional, List, Tuple, Dict, Iterable

from backend.database.client import get_supabase_client
from supabase import Client
from backend.shared.models import SearchQuery


logger = logging.getLogger(__name__)


def _group_rows_by_key(rows: Optional[List[dict]], key: str) -> Dict[int, List[dict]]:
    mapping: Dict[int, List[dict]] = defaultdict(list)
    if not rows:
        return mapping
    for row in rows:
        value = row.get(key)
        if value is None:
            continue
        try:
            mapping[int(value)].append(row)
        except (TypeError, ValueError):
            continue
    return mapping


def _fetch_related_by_company(
    client: Client,
    table: str,
    company_ids: List[int],
    *,
    order: Optional[Tuple[str, bool]] = None,
) -> Dict[int, List[dict]]:
    if not company_ids:
        return {}

    query = client.table(table).select("*")
    query = query.in_("company_id", company_ids)
    if order:
        column, desc = order
        query = query.order(column, desc=desc)

    response = query.execute()
    return _group_rows_by_key(response.data, "company_id")


def _fetch_links_map(client: Client, company_ids: List[int]) -> Dict[int, List[dict]]:
    if not company_ids:
        return {}

    mapping: Dict[int, List[dict]] = defaultdict(list)
    collected: Dict[int, dict] = {}

    for column in ("source_company_id", "target_company_id"):
        response = (
            client.table("links")
            .select("*")
            .in_(column, company_ids)
            .execute()
        )
        for row in response.data or []:
            row_id = row.get("id")
            if row_id in collected:
                continue
            collected[row_id] = row

    for row in collected.values():
        for column in ("source_company_id", "target_company_id"):
            company_id = row.get(column)
            if company_id in company_ids:
                mapping[int(company_id)].append(row)

    return mapping


def _resolve_company_ids_by_cities(
    client: Client, cities: Iterable[str]
) -> List[int]:
    city_list = [city.strip() for city in cities if city and city.strip()]
    if not city_list:
        return []

    response = (
        client.table("company_addresses")
        .select("company_id")
        .in_("city", city_list)
        .eq("is_active", True)
        .execute()
    )

    company_ids: List[int] = []
    seen: set[int] = set()
    for row in response.data or []:
        company_id = row.get("company_id")
        if company_id is None:
            continue
        try:
            cid = int(company_id)
        except (TypeError, ValueError):
            continue
        if cid not in seen:
            seen.add(cid)
            company_ids.append(cid)
    return company_ids

def get_all_companies(limit: int = 100, offset: int = 0) -> List[dict]:
    """Get all companies with pagination. Includes primary address for each company."""
    client = get_supabase_client()
    response = (
        client.table('companies')
        .select('*')
        .order('name')
        .range(offset, offset + limit - 1)
        .execute()
    )
    companies = response.data or []

    if not companies:
        return []

    company_ids: List[int] = []
    for record in companies:
        company_id = record.get('id')
        if company_id is None:
            continue
        try:
            company_ids.append(int(company_id))
        except (TypeError, ValueError):
            continue

    addresses_map = _fetch_related_by_company(client, 'company_addresses', company_ids)
    officers_map = _fetch_related_by_company(client, 'company_officers', company_ids)
    activities_map = _fetch_related_by_company(
        client, 'company_activities', company_ids, order=('created_at', True)
    )
    financials_map = _fetch_related_by_company(
        client, 'company_financials', company_ids, order=('year', True)
    )
    filings_map = _fetch_related_by_company(
        client, 'company_filings', company_ids, order=('date', True)
    )
    risks_map = _fetch_related_by_company(
        client, 'company_risks', company_ids, order=('date', True)
    )
    links_map = _fetch_links_map(client, company_ids)

    for company in companies:
        company_id = company.get('id')
        if company_id is None:
            continue
        try:
            cid = int(company_id)
        except (TypeError, ValueError):
            continue

        addresses = [addr for addr in addresses_map.get(cid, []) if addr.get('is_active', True)]
        company['addresses'] = addresses
        company['address'] = addresses[0] if addresses else None
        if addresses:
            company_city = addresses[0].get('city')
            if company_city:
                company['city'] = company_city

        company['officers'] = officers_map.get(cid, [])
        company['activities'] = activities_map.get(cid, [])
        company['financials'] = financials_map.get(cid, [])
        company['filings'] = filings_map.get(cid, [])
        company['risks'] = risks_map.get(cid, [])
        company['links'] = links_map.get(cid, [])

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


def create_company_with_relations(
    company_data: Dict[str, Any],
    *,
    addresses: Optional[List[Dict[str, Any]]] = None,
    officers: Optional[List[Dict[str, Any]]] = None,
    activities: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Create or update a company alongside its related records."""

    client = get_supabase_client()

    payload = dict(company_data)
    payload.setdefault("last_fetched_at", datetime.utcnow().isoformat())

    response = (
        client.table("companies")
        .upsert(payload, on_conflict="fnr")
        .execute()
    )
    if not response.data:
        raise ValueError("Failed to insert or update company record")

    company = response.data[0]
    company_id = company.get("id")
    if company_id is None:
        raise ValueError("Company record missing ID after upsert")

    _sync_related_records(
        client,
        company_id,
        addresses=addresses or [],
        officers=officers or [],
        activities=activities or [],
    )

    detailed_company = get_company_with_details(company_id)
    if detailed_company:
        return detailed_company

    # Fall back to returning the upsert result if detailed fetch failed.
    company.setdefault("officers", officers or [])
    company.setdefault("addresses", addresses or [])
    company.setdefault("activities", activities or [])
    return company


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


def _sync_related_records(
    client: Client,
    company_id: int,
    *,
    addresses: List[Dict[str, Any]],
    officers: List[Dict[str, Any]],
    activities: List[Dict[str, Any]],
) -> None:
    """Replace related records for a company with new data."""

    _replace_records(client, "company_addresses", company_id, addresses)
    _replace_records(client, "company_officers", company_id, officers)
    _replace_records(client, "company_activities", company_id, activities)


def _replace_records(
    client: Client,
    table: str,
    company_id: int,
    records: List[Dict[str, Any]],
) -> None:
    if not records:
        # Ensure we clear stale records even when no data is provided.
        try:
            client.table(table).delete().eq("company_id", company_id).execute()
        except Exception as exc:  # pragma: no cover - depends on Supabase configuration
            logger.debug("Skipping cleanup for %s: %s", table, exc)
        return

    try:
        client.table(table).delete().eq("company_id", company_id).execute()
    except Exception as exc:  # pragma: no cover
        logger.debug("Unable to clear %s for company %s: %s", table, company_id, exc)

    payload = []
    for record in records:
        item = dict(record)
        item["company_id"] = company_id
        payload.append(item)

    try:
        client.table(table).insert(payload).execute()
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to insert %s for company %s: %s", table, company_id, exc)


def _attach_company_relations(
    companies: List[dict], client: Client
) -> List[dict]:
    """Attach related officers and addresses to company records."""

    if not companies:
        return []

    company_ids: List[int] = []
    for company in companies:
        company_id = company.get("id")
        if company_id is None:
            continue
        try:
            company_ids.append(int(company_id))
        except (TypeError, ValueError):
            continue

    if not company_ids:
        return companies

    addresses_map = _fetch_related_by_company(client, "company_addresses", company_ids)
    officers_map = _fetch_related_by_company(client, "company_officers", company_ids)
    activities_map = _fetch_related_by_company(
        client, "company_activities", company_ids, order=("created_at", True)
    )
    financials_map = _fetch_related_by_company(
        client, "company_financials", company_ids, order=("year", True)
    )
    filings_map = _fetch_related_by_company(
        client, "company_filings", company_ids, order=("date", True)
    )
    risks_map = _fetch_related_by_company(
        client, "company_risks", company_ids, order=("date", True)
    )
    links_map = _fetch_links_map(client, company_ids)

    for company in companies:
        company_id = company.get("id")
        if company_id is None:
            continue
        try:
            cid = int(company_id)
        except (TypeError, ValueError):
            continue

        addresses = [addr for addr in addresses_map.get(cid, []) if addr.get("is_active", True)]
        company["addresses"] = addresses
        company["address"] = addresses[0] if addresses else None
        if addresses:
            city = addresses[0].get("city")
            if city:
                company["city"] = city

        company["officers"] = officers_map.get(cid, [])
        company["activities"] = activities_map.get(cid, [])
        company["financials"] = financials_map.get(cid, [])
        company["filings"] = filings_map.get(cid, [])
        company["risks"] = risks_map.get(cid, [])
        company["links"] = links_map.get(cid, [])

    return companies


def search_companies(
    query: str,
    limit: int = 50,
    offset: int = 0,
    city: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """Search companies by name or FNR with pagination.

    If ``city`` is provided, restrict results to companies whose primary
    city (stored on the ``companies`` table) matches exactly.
    """

    client = get_supabase_client()
    city_filtered_ids: Optional[List[int]] = None
    if city:
        city_filtered_ids = _resolve_company_ids_by_cities(client, [city])
        if not city_filtered_ids:
            return [], 0

    query_builder = (
        client.table("companies")
        .select("*", count="exact")
        .or_(f"name.ilike.%{query}%,fnr.ilike.%{query}%")
    )

    if city_filtered_ids is not None:
        query_builder = query_builder.in_("id", city_filtered_ids)

    response = query_builder.range(offset, offset + limit - 1).execute()

    companies = response.data or []

    # Attach related data
    if companies:
        companies = _attach_company_relations(companies, client)

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


def get_dashboard_stats() -> dict:
    """Return stats for the dashboard."""
    client = get_supabase_client()
    
    # Total companies
    total_companies = client.table("companies").select("id", count="exact").limit(1).execute().count or 0
    
    # Active companies
    active_companies = client.table("companies").select("id", count="exact").eq("state", "active").limit(1).execute().count or 0
    
    # Total officers
    total_officers = client.table("company_officers").select("id", count="exact").limit(1).execute().count or 0
    
    return {
        "total_companies": total_companies,
        "active_companies": active_companies,
        "total_officers": total_officers,
    }


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


def get_company_with_details_by_fnr(fnr: str) -> Optional[dict]:
    """Get a company and relations by Firmenbuch number."""

    company = get_company_by_fnr(fnr)
    if not company:
        return None
    company_id = company.get('id')
    if company_id is None:
        return company
    return get_company_with_details(company_id)


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


# Export queries
def create_export(export_data: dict) -> dict:
    """Create a new export record."""
    client = get_supabase_client()
    response = client.table('exports').insert(export_data).execute()
    return response.data[0] if response.data else None


def get_export_by_id(export_id: int) -> Optional[dict]:
    """Get an export by ID."""
    client = get_supabase_client()
    response = client.table('exports').select('*').eq('id', export_id).execute()
    return response.data[0] if response.data else None


def get_exports_by_company(company_id: int, limit: int = 50) -> List[dict]:
    """Get all exports for a company."""
    client = get_supabase_client()
    response = client.table('exports').select('*').eq('company_id', company_id).order('exported_at', desc=True).limit(limit).execute()
    return response.data or []
