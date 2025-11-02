#!/usr/bin/env python3
"""
Startup script for BizRay FastAPI backend.
"""
import uvicorn
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("Starting BizRay API Server...")
    print("API Documentation: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("Health Check: http://localhost:8000/health")
    print("\n")
    
    uvicorn.run(
        "services.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
