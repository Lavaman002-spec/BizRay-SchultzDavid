from supabase import create_client, Client
from functools import lru_cache
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import SUPABASE_URL, SUPABASE_KEY


@lru_cache()
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
        )
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_db() -> Client:
    return get_supabase_client()
