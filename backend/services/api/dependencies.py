"""FastAPI dependencies."""
from typing import Annotated
from fastapi import Depends
from supabase import Client
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.client import get_db


# Type alias for database dependency
DatabaseDep = Annotated[Client, Depends(get_db)]
