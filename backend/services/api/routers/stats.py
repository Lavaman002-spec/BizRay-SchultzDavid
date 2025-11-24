from fastapi import APIRouter, HTTPException
from backend.database import queries as db_queries
from backend.shared.models import DashboardStats

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/", response_model=DashboardStats)
async def get_stats():
    """Get dashboard statistics."""
    try:
        stats = db_queries.get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")
