import sys
from pathlib import Path

import uvicorn

backend_dir = Path(__file__).resolve().parent
repo_root = backend_dir.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

if __name__ == "__main__":
    print("Starting BizRay API Server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("\n")
    
    uvicorn.run(
        "backend.services.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
