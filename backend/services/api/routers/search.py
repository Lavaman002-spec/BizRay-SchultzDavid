"""API routes for search functionality."""
from typing import List, Optional
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
    fetch_company_suggestions_from_firmenbuch,
    fetch_company_profile_by_name_if_missing,
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

        if not companies and offset == 0:
            fetched_company = None
            if validate_fn_number(query):
                fnr = normalize_fn_number(query)
                try:
                    fetched = fetch_company_profile_if_missing(fnr)
                except FirmenbuchCompanyNotFound:
                    logger.info(
                        "Firmenbuch record %s not found during search fallback", fnr
                    )
                except FirmenbuchFetchError as exc:
                    logger.warning(
                        "Firmenbuch fetch failed for %s during search: %s", fnr, exc
                    )
                else:
                    fetched_company = (
                        db_queries.get_company_with_details_by_fnr(fnr) or fetched
                    )
            else:
                try:
                    fetched = fetch_company_profile_by_name_if_missing(query)
                except FirmenbuchCompanyNotFound:
                    logger.info(
                        "No Firmenbuch records found for name '%s' during search fallback",
                        query,
                    )
                except FirmenbuchFetchError as exc:
                    logger.warning(
                        "Firmenbuch name search failed for '%s' during search: %s",
                        query,
                        exc,
                    )
                else:
                    fnr = fetched.get("fnr")
                    if fnr:
                        fetched_company = (
                            db_queries.get_company_with_details_by_fnr(fnr) or fetched
                        )
                    else:
                        fetched_company = fetched

            if fetched_company:
                companies = [fetched_company]
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

        if not suggestions:
            remote_suggestions: List[dict] = []
            try:
                remote_suggestions = fetch_company_suggestions_from_firmenbuch(
                    query, limit=limit
                )
            except FirmenbuchCompanyNotFound:
                logger.info(
                    "No Firmenbuch suggestions found for '%s'", query,
                )
            except FirmenbuchFetchError as exc:
                logger.warning(
                    "Firmenbuch suggestion lookup failed for '%s': %s", query, exc
                )
            else:
                refreshed = db_queries.get_search_suggestions(query, limit=limit)
                if refreshed:
                    suggestions = refreshed
                else:
                    suggestions = remote_suggestions

        return SearchSuggestionsResponse(query=query, suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion lookup failed: {str(e)}")

