from fastapi import APIRouter, HTTPException
from datetime import datetime

from backend.database import queries as db_queries
from backend.shared.models import ExportCreate, Export

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/", response_model=Export)
async def create_export(export_data: ExportCreate):
    """
    Create a new export record for a company.
    This endpoint is called when a user exports a company report.
    """
    # Verify the company exists
    company = db_queries.get_company_by_id(export_data.company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ID {export_data.company_id} not found")

    # Create the export record
    export_record = db_queries.create_export(export_data.model_dump())
    if not export_record:
        raise HTTPException(status_code=500, detail="Failed to create export record")

    return export_record


@router.get("/{export_id}", response_model=Export)
async def get_export(export_id: int):
    """
    Get an export record by ID.
    """
    export_record = db_queries.get_export_by_id(export_id)
    if not export_record:
        raise HTTPException(status_code=404, detail=f"Export with ID {export_id} not found")

    return export_record


@router.get("/company/{company_id}")
async def get_company_exports(company_id: int, limit: int = 50):
    """
    Get all export records for a company.
    """
    exports = db_queries.get_exports_by_company(company_id, limit)
    return exports
