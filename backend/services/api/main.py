from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import search, companies  # Import search BEFORE companies

app = FastAPI(
    title="BizRay API",
    description="Austrian Business Register Data API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - search BEFORE companies (more specific routes first)
app.include_router(search.router)
app.include_router(companies.router)

@app.get("/")
def root():
    return {"message": "BizRay API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}