"""API routes for location functionality."""
from typing import List

from fastapi import APIRouter, HTTPException

from backend.database import queries as db_queries

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/cities", response_model=List[str])
async def get_cities():
    """
    Get all unique cities from company addresses.
    Returns a sorted list of city names.
    """
    try:
        cities = db_queries.get_unique_cities()
        return cities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cities: {str(e)}")
