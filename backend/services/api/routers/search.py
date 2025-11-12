"""API routes for search functionality."""
from typing import Optional
import logging
from fastapi import APIRouter, HTTPException, Query
from shared.models import (
    SearchQuery,
    SearchResponse,
    SearchSuggestionsResponse,
)
from database import queries as db_queries
from services.ingest.api_fetch import (
    FirmenbuchCompanyNotFound,
    FirmenbuchFetchError,
    fetch_company_profile_if_missing,
)
from shared.utils import normalize_fn_number, validate_fn_number


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
async def search_companies(
    query: str = Query(..., min_length=1, description="Search query for company name or FNR"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    city: Optional[str] = Query(None, description="Filter by city")
):
    """
    Search for companies by name or Firmenbuch number (FNR).
    Optionally filter by city.
    """
    try:
        companies, total = db_queries.search_companies(query.strip(), limit=limit, offset=offset)

        if not companies and offset == 0 and validate_fn_number(query):
            fnr = normalize_fn_number(query)
            try:
                fetch_company_profile_if_missing(fnr)
            except FirmenbuchCompanyNotFound:
                logger.info("Firmenbuch record %s not found during search fallback", fnr)
            except FirmenbuchFetchError as exc:
                logger.warning("Firmenbuch fetch failed for %s during search: %s", fnr, exc)
            else:
                company = db_queries.get_company_with_details_by_fnr(fnr)
                if company:
                    companies = [company]
                    total = 1

        has_more = offset + len(companies) < total
        next_offset = offset + len(companies) if has_more else None

        return SearchResponse(
            total=total,
            count=len(companies),
            results=companies,
            limit=limit,
            offset=offset,
            next_offset=next_offset,
            has_more=has_more,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/", response_model=SearchResponse)
async def search_companies_advanced(payload: SearchQuery):
    """Perform an advanced search that supports filters, sorting and pagination."""

    try:
        companies, total = db_queries.search_companies_advanced(payload)

        limit = payload.pagination.limit
        offset = payload.pagination.offset
        has_more = offset + len(companies) < total
        next_offset = offset + len(companies) if has_more else None

        return SearchResponse(
            total=total,
            count=len(companies),
            results=companies,
            limit=limit,
            offset=offset,
            next_offset=next_offset,
            has_more=has_more,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced search failed: {str(e)}")


@router.get("/suggest", response_model=SearchSuggestionsResponse)
async def search_suggestions(
    query: str = Query(..., min_length=1, description="Prefix used to suggest matching companies"),
    limit: int = Query(10, ge=1, le=25),
):
    """Return autocomplete suggestions for the provided query prefix."""

    try:
        suggestions = db_queries.get_search_suggestions(query, limit=limit)
        return SearchSuggestionsResponse(query=query, suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion lookup failed: {str(e)}")

