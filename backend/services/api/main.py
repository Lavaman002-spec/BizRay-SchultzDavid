from datetime import datetime
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.shared.models import HealthCheck
from backend.database.client import get_db
from backend.database.queries import health_check
from backend.services.api.routers import (
    companies,
    officers,
    search,
    locations,
    exports,
)


# Initialize FastAPI app
app = FastAPI(
    title="BizRay API",
    description="Austrian Business Register (Firmenbuch) API - Search and manage company data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(companies.router, prefix="/api")
app.include_router(officers.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(exports.router, prefix="/api")

@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information."""
    return {
        "message": "BizRay API is running",
        "name": "BizRay API",
        "version": "1.0.0",
        "description": "Austrian Business Register (Firmenbuch) API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health():
    """Health check endpoint."""
    db = get_db()
    db_status = "connected" if health_check(db) else "disconnected"
    
    return HealthCheck(
        status="healthy" if db_status == "connected" else "unhealthy",
        timestamp=datetime.now(),
        database=db_status
    )


@app.get("/api", tags=["api"])
async def api_info():
    """API information and available endpoints."""
    return {
        "version": "1.0.0",
        "endpoints": {
            "companies": "/api/companies",
            "officers": "/api/officers",
            "search": "/api/search",
            "exports": "/api/exports",
            "locations": "/api/locations",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
