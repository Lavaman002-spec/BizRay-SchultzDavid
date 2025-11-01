"""
Start script for BizRay API server.
Handles Python path configuration automatically.
"""
import sys
import os

# Add services/api to Python path
api_path = os.path.join(os.path.dirname(__file__), 'services', 'api')
sys.path.insert(0, api_path)

# Now import and run uvicorn
import uvicorn

if __name__ == "__main__":
    # Change to the API directory
    os.chdir(api_path)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[api_path]
    )