import logging
from functools import lru_cache
import os
import sys

from supabase import Client, create_client

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import SUPABASE_KEY, SUPABASE_URL


logger = logging.getLogger(__name__)


class _DummyResponse:
    def __init__(self):
        self.data = []
        self.count = 0


class _DummyQueryBuilder:
    def __getattr__(self, _name):
        def _method(*_args, **_kwargs):
            return self

        return _method

    def execute(self):
        return _DummyResponse()


class _DummySupabaseClient:
    def table(self, *_args, **_kwargs):
        return _DummyQueryBuilder()


@lru_cache()
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning(
            "SUPABASE_URL and SUPABASE_KEY not configured; using dummy Supabase client"
        )
        return _DummySupabaseClient()  # type: ignore[return-value]

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_db() -> Client:
    return get_supabase_client()
