from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
import json
import os

from database import queries as db_queries

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/{id}")
async def export_data(id: int):
    """
    Generate an export file for the given export ID.
    The file includes a timestamp, data versions, a parameter block,
    and the export data retrieved from the database.
    """
    # 1. Get export record from database
    export_record = db_queries.get_export_by_id(id)
    if not export_record:
        raise HTTPException(status_code=404, detail=f"Export with ID {id} not found")

    # 2. Prepare metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_versions = {
        "schema_version": "1.0.0",
        "data_version": datetime.now().strftime("%Y.%m.%d"),
    }
    param_block = {
        "requested_id": id,
        "export_type": "standard",
        "generated_by": "BizRay API",
        "generated_at": timestamp,
    }

    # 3. Build export content
    export_content = {
        "timestamp": timestamp,
        "data_versions": data_versions,
        "param_block": param_block,
        "data": export_record,  # directly from DB
    }

    # 4. Create output directory (if needed)
    output_dir = "/tmp/exports"
    os.makedirs(output_dir, exist_ok=True)

    # 5. Generate file name and path
    filename = f"export_{id}_{timestamp}.json"
    file_path = os.path.join(output_dir, filename)

    # 6. Write file to disk
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_content, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write export file: {str(e)}")

    # 7. Return the file to the client
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/json",
        headers={"X-Export-Generated": timestamp},
    )