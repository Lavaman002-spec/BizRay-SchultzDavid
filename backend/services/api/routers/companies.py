"""API routes for companies."""
from typing import List
from fastapi import APIRouter, HTTPException, Query
from shared.models import Company, CompanyCreate, CompanyUpdate, CompanyWithDetails
from database import queries as db_queries

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=List[Company])
async def get_companies(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all companies with pagination."""
    try:
        companies = db_queries.get_all_companies(limit=limit, offset=offset)
        return companies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch companies: {str(e)}")


@router.get("/{company_id}", response_model=CompanyWithDetails)
async def get_company(company_id: int):
    """Get a specific company by ID with its officers and addresses."""
    try:
        company = db_queries.get_company_with_details(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch company: {str(e)}")


@router.get("/fnr/{fnr}", response_model=Company)
async def get_company_by_fnr(fnr: str):
    """Get a company by its Firmenbuch number."""
    company = db_queries.get_company_by_fnr(fnr)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with FNR {fnr} not found")
    return company


@router.post("/", response_model=Company, status_code=201)
async def create_company(company: CompanyCreate):
    """Create a new company."""
    try:
        new_company = db_queries.create_company(company.model_dump(exclude_unset=True))
        return new_company
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create company: {str(e)}")


@router.put("/{company_id}", response_model=Company)
async def update_company(company_id: int, company: CompanyUpdate):
    """Update a company."""
    existing_company = db_queries.get_company_by_id(company_id)
    if not existing_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        updated_company = db_queries.update_company(
            company_id, 
            company.model_dump(exclude_unset=True)
        )
        return updated_company
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update company: {str(e)}")


@router.delete("/{company_id}", status_code=204)
async def delete_company(company_id: int):
    """Delete a company."""
    existing_company = db_queries.get_company_by_id(company_id)
    if not existing_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        db_queries.delete_company(company_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete company: {str(e)}")