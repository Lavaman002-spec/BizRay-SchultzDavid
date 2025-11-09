"""API routes for search functionality."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from shared.models import SearchResponse
from database import queries as db_queries

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
        results = db_queries.search_companies(
            query.strip(),
            limit=limit,
            city=city.strip() if city else None
        )

        return SearchResponse(
            total=len(results),
            results=results,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/suggestions", response_model=List[str])
async def get_suggestions(
    query: str = Query(..., min_length=1, description="Partial company name for autocomplete"),
    limit: int = Query(10, ge=1, le=20)
):
    """
    Get company name suggestions for autocomplete.
    Returns a list of company names that match the partial query.
    """
    try:
        suggestions = db_queries.get_company_name_suggestions(query.strip(), limit=limit)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch suggestions: {str(e)}")

