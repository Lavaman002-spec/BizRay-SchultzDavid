"""API routes for officers."""
from typing import List

from fastapi import APIRouter, HTTPException, Query

from backend.database.client import get_supabase_client
from backend.shared.models import Officer, OfficerCreate, OfficerUpdate

router = APIRouter(prefix="/officers", tags=["officers"])


@router.get("/", response_model=List[Officer])
async def get_officers(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all officers with pagination."""
    try:
        client = get_supabase_client()
        response = client.table('company_officers').select('*').range(offset, offset + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch officers: {str(e)}")


@router.get("/{officer_id}", response_model=Officer)
async def get_officer(officer_id: int):
    """Get a specific officer by ID."""
    try:
        client = get_supabase_client()
        response = client.table('company_officers').select('*').eq('id', officer_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Officer not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch officer: {str(e)}")


@router.get("/company/{company_id}", response_model=List[Officer])
async def get_officers_by_company(company_id: int):
    """Get all officers for a specific company."""
    try:
        client = get_supabase_client()
        response = client.table('company_officers').select('*').eq('company_id', company_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch officers: {str(e)}")


@router.post("/", response_model=Officer, status_code=201)
async def create_officer(officer: OfficerCreate):
    """Create a new officer."""
    try:
        client = get_supabase_client()
        response = client.table('company_officers').insert(officer.model_dump(exclude_unset=True)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create officer: {str(e)}")


@router.put("/{officer_id}", response_model=Officer)
async def update_officer(officer_id: int, officer: OfficerUpdate):
    """Update an officer."""
    try:
        client = get_supabase_client()
        # Check if officer exists
        existing = client.table('company_officers').select('*').eq('id', officer_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        response = client.table('company_officers').update(officer.model_dump(exclude_unset=True)).eq('id', officer_id).execute()
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update officer: {str(e)}")


@router.delete("/{officer_id}", status_code=204)
async def delete_officer(officer_id: int):
    """Delete an officer."""
    try:
        client = get_supabase_client()
        # Check if officer exists
        existing = client.table('company_officers').select('*').eq('id', officer_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        client.table('company_officers').delete().eq('id', officer_id).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete officer: {str(e)}")
