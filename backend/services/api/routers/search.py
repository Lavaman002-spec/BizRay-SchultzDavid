from fastapi import APIRouter, Query
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import conn
from models import SearchResponse, SearchResultItem

router = APIRouter(tags=["search"])

@router.get("/companies/search", response_model=SearchResponse)
def search_companies(
    q: str = Query("", description="Company name or register id"),
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    city: Optional[str] = None,
):
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
        return SearchResponse(total=total, items=items)
    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        raise