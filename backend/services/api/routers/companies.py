from fastapi import APIRouter, HTTPException, Response
import csv, io, datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import conn
from models import CompanyIdentity, CompanyProfile, Officer

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/{company_id}", response_model=CompanyProfile)
def get_company(company_id: str):
    try:
        with conn() as c:
            cur = c.cursor()
            cur.execute("""
                SELECT id, register_id, name, legal_form, status, address_line, city, country
                FROM companies WHERE id=%s
            """, (company_id,))
            comp = cur.fetchone()
            
            if not comp:
                raise HTTPException(status_code=404, detail="Company not found")
            
            cur.execute("""
                SELECT person_id, person_name, role FROM officers WHERE company_id=%s
            """, (company_id,))
            offs = cur.fetchall()
            cur.close()
        
        identity = CompanyIdentity(
            id=str(comp[0]), 
            register_id=comp[1], 
            name=comp[2], 
            legal_form=comp[3],
            status=comp[4], 
            address_line=comp[5], 
            city=comp[6], 
            country=comp[7]
        )
        officers = [Officer(person_id=o[0], person_name=o[1], role=o[2]) for o in offs]
        return CompanyProfile(identity=identity, addresses=[], officers=officers, owners=[], filings=[])
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get company error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exports/{company_id}")
def export_company_csv(company_id: str):
    try:
        with conn() as c:
            cur = c.cursor()
            cur.execute("""
                SELECT id, register_id, name, legal_form, status, address_line, city, country
                FROM companies WHERE id=%s
            """, (company_id,))
            comp = cur.fetchone()
            
            cur.execute("""
                SELECT person_id, person_name, role FROM officers WHERE company_id=%s
            """, (company_id,))
            offs = cur.fetchall()
            cur.close()
        
        if not comp:
            raise HTTPException(status_code=404, detail="Company not found")

        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["export_timestamp", datetime.datetime.utcnow().isoformat()+"Z"])
        w.writerow(["section", "identity"])
        w.writerow(["id","register_id","name","legal_form","status","address_line","city","country"])
        w.writerow(list(comp))
        w.writerow([])
        w.writerow(["section","officers"])
        w.writerow(["person_id","person_name","role"])
        for o in offs:
            w.writerow(list(o))
        data = buf.getvalue()
        return Response(content=data, media_type="text/csv",
                        headers={"Content-Disposition": f'attachment; filename="company_{company_id}.csv"'})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))