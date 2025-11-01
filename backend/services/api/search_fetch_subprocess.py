"""
Search and Fetch Subprocess Wrapper

This module provides a subprocess-based interface to the search_and_fetch CLI tool.
It avoids import conflicts by running the search tool in a separate process.
"""

import subprocess
import json
import os
from typing import Dict, List, Optional


def search_and_fetch(
    query: str,
    fetch_if_not_found: bool = True,
    max_api_results: int = 5,
    max_to_fetch: int = 1
) -> Dict:
    """
    Search for companies using the CLI tool via subprocess.
    
    Args:
        query: Company name to search for
        fetch_if_not_found: Whether to fetch from API if not in database
        max_api_results: Maximum API search results to consider
        max_to_fetch: Maximum companies to fetch from API
        
    Returns:
        dict: {
            'local_results': List of companies found in database,
            'api_results': List of companies found in API,
            'fetched': List of companies that were fetched and added,
            'success': bool,
            'error': Optional error message
        }
    """
    try:
        # Path to the search script - use absolute path in container
        if os.path.exists("/bizray/backend/services/ingest/search_company.py"):
            script_dir = "/bizray/backend/services/ingest"
            script_path = "/bizray/backend/services/ingest/search_company.py"
        else:
            # Fallback for local development
            script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../ingest"))
            script_path = os.path.join(script_dir, "search_company.py")
        
        # Build command
        cmd = ["python3", script_path, query]
        
        if not fetch_if_not_found:
            cmd.append("--no-fetch")
        
        cmd.extend(["--max-results", str(max_api_results)])
        cmd.extend(["--max-fetch", str(max_to_fetch)])
        
        # Run subprocess
        result = subprocess.run(
            cmd,
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Parse output - look for the JSON data structure
        # For now, we'll parse the text output
        output = result.stdout
        
        # Extract results from output
        local_results = []
        fetched = []
        
        # Simple parsing - look for company names in output
        if "✅ Found" in output and "companies in database:" in output:
            # Companies found locally
            lines = output.split('\n')
            in_results = False
            for i, line in enumerate(lines):
                if "✅ Found" in line and "companies in database:" in line:
                    in_results = True
                    continue
                if in_results and line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                    # Extract company name
                    name = line.split('.', 1)[1].strip()
                    local_results.append({'name': name})
                if "⬇️  FETCHED AND STORED:" in line:
                    break
        
        if "⬇️  FETCHED AND STORED:" in output:
            lines = output.split('\n')
            in_fetched = False
            for line in lines:
                if "⬇️  FETCHED AND STORED:" in line:
                    in_fetched = True
                    continue
                if in_fetched and line.strip().startswith('✓'):
                    # Extract fetched company
                    name = line.split('✓')[1].strip()
                    if '(' in name:
                        name = name.split('(')[0].strip()
                    fetched.append({'name': name})
                if "=" * 40 in line and in_fetched:
                    break
        
        return {
            'local_results': local_results,
            'api_results': [],
            'fetched': fetched,
            'success': result.returncode == 0,
            'error': result.stderr if result.returncode != 0 else None,
            'output': output  # Include full output for debugging
        }
        
    except subprocess.TimeoutExpired:
        return {
            'local_results': [],
            'api_results': [],
            'fetched': [],
            'success': False,
            'error': 'Search timeout - request took longer than 30 seconds'
        }
    except Exception as e:
        return {
            'local_results': [],
            'api_results': [],
            'fetched': [],
            'success': False,
            'error': str(e)
        }


def is_available() -> bool:
    """Check if the search_company.py script is available."""
    try:
        # Check absolute path first (container)
        if os.path.exists("/bizray/backend/services/ingest/search_company.py"):
            return True
        # Fallback for local development
        script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../ingest"))
        script_path = os.path.join(script_dir, "search_company.py")
        return os.path.exists(script_path)
    except Exception:
        return False
