"""FastAPI dependencies."""
import sys
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from supabase import Client

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.database.client import get_db


# Type alias for database dependency
DatabaseDep = Annotated[Client, Depends(get_db)]
