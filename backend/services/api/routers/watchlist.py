from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from backend.services.api.dependencies import DatabaseDep, CurrentUserDep

router = APIRouter(
    prefix="/watchlist",
    tags=["watchlist"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_watchlist(
    db: DatabaseDep,
    current_user: CurrentUserDep
):
    """Get the current user's watchlist."""
    user_id = current_user.id
    response = db.table("user_watchlist").select("*, company:companies(*)").eq("user_id", user_id).execute()
    return response.data

@router.post("/{company_id}")
async def add_to_watchlist(
    company_id: int,
    db: DatabaseDep,
    current_user: CurrentUserDep
):
    """Add a company to the watchlist."""
    user_id = current_user.id
    
    # Check if company exists
    company = db.table("companies").select("id").eq("id", company_id).execute()
    if not company.data:
        raise HTTPException(status_code=404, detail="Company not found")

    try:
        response = db.table("user_watchlist").insert({
            "user_id": user_id,
            "company_id": company_id
        }).execute()
        return response.data[0]
    except Exception as e:
        # Likely unique constraint violation
        raise HTTPException(status_code=400, detail="Company already in watchlist")

@router.delete("/{company_id}")
async def remove_from_watchlist(
    company_id: int,
    db: DatabaseDep,
    current_user: CurrentUserDep
):
    """Remove a company from the watchlist."""
    user_id = current_user.id
    response = db.table("user_watchlist").delete().eq("user_id", user_id).eq("company_id", company_id).execute()
    return {"success": True}

@router.get("/check/{company_id}")
async def check_watchlist(
    company_id: int,
    db: DatabaseDep,
    current_user: CurrentUserDep
):
    """Check if a company is in the watchlist."""
    user_id = current_user.id
    response = db.table("user_watchlist").select("id").eq("user_id", user_id).eq("company_id", company_id).execute()
    return {"is_watched": len(response.data) > 0}
