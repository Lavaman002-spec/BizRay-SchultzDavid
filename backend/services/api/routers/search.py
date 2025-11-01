from fastapi import APIRouter, Query
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import conn
from models import SearchResponse, SearchResultItem

router = APIRouter(tags=["search"])

# Import subprocess-based search and fetch
try:
    from ..search_fetch_subprocess import search_and_fetch, is_available
    SEARCH_AND_FETCH_AVAILABLE = is_available()
    if SEARCH_AND_FETCH_AVAILABLE:
        print("✓ search_and_fetch (subprocess) available")
    else:
        print("⚠️  search_and_fetch script not found")
except ImportError as e:
    SEARCH_AND_FETCH_AVAILABLE = False
    print(f"⚠️  search_and_fetch module not available: {e}")
    
    # Fallback - create dummy function
    def search_and_fetch(*args, **kwargs):
        return {'local_results': [], 'api_results': [], 'fetched': [], 'success': False}

@router.get("/companies/search", response_model=SearchResponse)
def search_companies(
    q: str = Query("", description="Company name or register id"),
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    city: Optional[str] = None,
    fetch_if_not_found: bool = Query(False, description="Fetch from API if not found in database"),
):
    """
    Search for companies in the database.
    
    If fetch_if_not_found=true and no results found, will search the
    Austrian Business Register API and fetch the company data.
    """
    q_like = f"%{q}%"
    where = ["1=1"]
    params = []

    if q:
        where.append("(name ILIKE %s OR register_id ILIKE %s)")
        params.extend([q_like, q_like])
    if status:
        where.append("status = %s")
        params.append(status)
    if city:
        where.append("city ILIKE %s")
        params.append(f"%{city}%")

    where_sql = " AND ".join(where)

    try:
        with conn() as c:
            cur = c.cursor()
            cur.execute(f"SELECT count(*) FROM companies WHERE {where_sql}", params)
            total = cur.fetchone()[0]
            
            cur.execute(
                f"""
                SELECT id, register_id, name, city, status
                FROM companies
                WHERE {where_sql}
                ORDER BY name ASC
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = cur.fetchall()
            cur.close()

        items = [SearchResultItem(id=str(r[0]), register_id=r[1], name=r[2], city=r[3], status=r[4]) for r in rows]
        
        # If no results found and fetch_if_not_found is enabled, try API search
        if total == 0 and fetch_if_not_found and SEARCH_AND_FETCH_AVAILABLE and q:
            print(f"🔍 No results for '{q}' - searching API via subprocess...")
            try:
                result = search_and_fetch(
                    query=q,
                    fetch_if_not_found=True,
                    max_api_results=5,
                    max_to_fetch=1  # Fetch only top match
                )
                
                # Check if subprocess was successful
                if result.get('success'):
                    # If we fetched something, re-query the database
                    if result.get('fetched'):
                        print(f"✓ Fetched {len(result['fetched'])} companies from API")
                        with conn() as c:
                            cur = c.cursor()
                            cur.execute(f"SELECT count(*) FROM companies WHERE {where_sql}", params)
                            total = cur.fetchone()[0]
                            
                            cur.execute(
                                f"""
                                SELECT id, register_id, name, city, status
                                FROM companies
                                WHERE {where_sql}
                                ORDER BY name ASC
                                LIMIT %s OFFSET %s
                                """,
                                params + [limit, offset],
                            )
                            rows = cur.fetchall()
                            cur.close()
                        
                        items = [SearchResultItem(id=str(r[0]), register_id=r[1], name=r[2], city=r[3], status=r[4]) for r in rows]
                    elif result.get('local_results'):
                        print(f"✓ Found {len(result['local_results'])} results after subprocess search")
                else:
                    print(f"⚠️  API search subprocess failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"⚠️  API search failed: {e}")
                import traceback
                traceback.print_exc()
                # Continue with empty results
        
        return SearchResponse(total=total, items=items)
    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        raise