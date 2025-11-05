"""API routes for search functionality."""
from fastapi import APIRouter, HTTPException, Query
from shared.models import (
    SearchQuery,
    SearchResponse,
    SearchSuggestionsResponse,
)
from database import queries as db_queries

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
async def search_companies(
    query: str = Query(..., min_length=1, description="Search query for company name or FNR"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Search for companies by name or Firmenbuch number (FNR).
    """
    try:
        companies, total = db_queries.search_companies(query.strip(), limit=limit, offset=offset)

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

