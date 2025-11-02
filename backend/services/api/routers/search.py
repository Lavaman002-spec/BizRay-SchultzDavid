"""API routes for search functionality."""
from fastapi import APIRouter, HTTPException, Query
from shared.models import SearchResponse
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
        results = db_queries.search_companies(query.strip(), limit=limit)
        
        return SearchResponse(
            total=len(results),
            results=results,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

