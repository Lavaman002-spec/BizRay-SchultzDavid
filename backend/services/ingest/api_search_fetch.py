"""
API Search and Fetch Wrapper

This module provides a simplified interface for the API to search and fetch companies.
It handles all the path management and imports internally.
"""

import sys
import os
import importlib.util

# Load the search_and_fetch module explicitly to avoid import conflicts
etl_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "etl"))
search_fetch_path = os.path.join(etl_dir, "search_and_fetch.py")

# Load module using importlib to avoid sys.path conflicts
spec = importlib.util.spec_from_file_location("_etl_search_and_fetch", search_fetch_path)
_search_fetch_module = importlib.util.module_from_spec(spec)
sys.modules['_etl_search_and_fetch'] = _search_fetch_module
spec.loader.exec_module(_search_fetch_module)

_search_and_fetch = _search_fetch_module.search_and_fetch


def search_and_fetch(query: str, fetch_if_not_found: bool = True, 
                      max_api_results: int = 5, max_to_fetch: int = 1):
    """
    Search for companies locally and optionally fetch from API if not found.
    
    Args:
        query: Company name to search for
        fetch_if_not_found: Whether to fetch from API if not in database
        max_api_results: Maximum API search results to consider
        max_to_fetch: Maximum companies to fetch from API
        
    Returns:
        dict: {
            'local_results': List of companies found in database,
            'api_results': List of companies found in API (if fetch_if_not_found),
            'fetched': List of companies that were fetched and added to database
        }
    """
    return _search_and_fetch(
        query=query,
        fetch_if_not_found=fetch_if_not_found,
        max_api_results=max_api_results,
        max_to_fetch=max_to_fetch
    )
