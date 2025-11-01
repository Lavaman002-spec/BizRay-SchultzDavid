import os
import json
import sys
from datetime import date, datetime
from zeep.helpers import serialize_object

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from client import create_client
from db import get_connection


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles date and datetime objects."""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def suche_firma(params: dict):
    """
    Run SUCHEFIRMA with the given params (dict).
    Returns the serialized response (native python types) or None on error.
    """
    client = create_client()
    try:
        resp = client.service.SUCHEFIRMA(**params)
        return serialize_object(resp)
    except Exception as e:
        print(f"API fetch failed (SUCHEFIRMA): {e}")
        return None

def suche_urkunde(fnr: str):
    """
    Run SUCHEURKUNDE for the given FNR (or register id) and return serialized response.
    """
    client = create_client()
    try:
        resp = client.service.SUCHEURKUNDE(FNR=fnr)
        return serialize_object(resp)
    except Exception as e:
        print(f"API fetch failed (SUCHEURKUNDE): {e}")
        return None

def urkunde(key: str):
    """
    Request URKUNDE by KEY (document key) and return serialized response.
    """
    client = create_client()
    try:
        resp = client.service.URKUNDE(KEY=key)
        return serialize_object(resp)
    except Exception as e:
        print(f"API fetch failed (URKUNDE): {e}")
        return None

def auszug_v2(fnr: str, umfang: str = "Kurzinformation"):
    """
    Request AUSZUG_V2_ (company extract) for the given FNR.
    Returns serialized response or None on error.
    
    Args:
        fnr: Company register number (e.g., "348406m", "FN348406")
        umfang: Scope of information ("Kurzinformation", "Normalinformation", etc.)
    """
    client = create_client()
    try:
        params = {
            "FNR": fnr,
            "STICHTAG": date.today().isoformat(),
            "UMFANG": umfang
        }
        resp = client.service.AUSZUG_V2_(**params)
        return serialize_object(resp)
    except Exception as e:
        print(f"API fetch failed (AUSZUG_V2_): {e}")
        return None


def fetch_company(register_id: str):
    """
    High-level function to fetch complete company data and store in staging tables.
    
    This function:
    1. Uses SUCHEURKUNDE to search by FNR directly (more reliable)
    2. Fetches detailed company information (Auszug)
    3. Inserts data into staging tables (stg_companies, stg_officers, stg_links)
    4. Returns structured company data
    
    Args:
        register_id: Company register ID (e.g., "FN348406", "348406m")
        
    Returns:
        dict with company data or None on error
    """
    print(f"→ Fetching company: {register_id}")
    
    # Normalize register_id format (remove "FN" prefix if present)
    fnr = register_id.replace("FN", "").strip()
    
    try:
        # Use SUCHEURKUNDE to find documents for this company
        search_result = suche_urkunde(fnr)
        
        if not search_result or not search_result.get('ERGEBNIS'):
            print(f"⚠️ No documents found for: {register_id}")
            print(f"   Trying alternative approach with AUSZUG_V2_ directly...")
            
            # Try to get company info directly via AUSZUG_V2_
            auszug_data = auszug_v2(fnr)
            if not auszug_data:
                print(f"⚠️ No company data found for: {register_id}")
                return None
            
            # Parse company data from Auszug
            company_data = _parse_company_from_auszug(auszug_data, fnr)
        else:
            # Get company info from search result
            first_result = search_result['ERGEBNIS'][0]
            
            # Fetch detailed information
            auszug_data = auszug_v2(fnr)
            
            # Parse and structure the data
            company_data = _parse_company_from_auszug(auszug_data, fnr)
        
        if not company_data:
            print(f"⚠️ Could not parse company data for: {register_id}")
            return None
        
        # Insert into staging tables
        _insert_into_staging(company_data)
        
        print(f"✓ Successfully fetched and staged: {company_data['name']}")
        return company_data
        
    except Exception as e:
        print(f"❌ Error fetching company {register_id}: {e}")
        import traceback
        traceback.print_exc()
        return None


def _parse_company_from_auszug(auszug_data: dict, register_id: str):
    """
    Parse company data from AUSZUG_V2_ response.
    
    Args:
        auszug_data: Company extract from AUSZUG_V2_
        register_id: The register ID
    
    Returns:
        dict with structured company data
    """
    if not auszug_data:
        return None
    
    # Extract basic company information from Auszug
    name = "Unknown Company"
    legal_form = ""
    status = "AKTIV"
    address_line = ""
    city = ""
    
    # THE KEY FIX: Company name is under auszug_data['FIRMA']['FI_DKZ02']
    if isinstance(auszug_data, dict):
        # Extract company name from FIRMA section
        if 'FIRMA' in auszug_data and isinstance(auszug_data['FIRMA'], dict):
            firma = auszug_data['FIRMA']
            
            # Get company name from FI_DKZ02
            if 'FI_DKZ02' in firma:
                fi_dkz02 = firma['FI_DKZ02']
                if isinstance(fi_dkz02, list) and fi_dkz02:
                    bezeichnung = fi_dkz02[0].get('BEZEICHNUNG', [])
                    if isinstance(bezeichnung, list) and bezeichnung:
                        name = bezeichnung[0]
                    elif bezeichnung:
                        name = str(bezeichnung)
            
            # Get address from FI_DKZ03
            if 'FI_DKZ03' in firma:
                fi_dkz03 = firma['FI_DKZ03']
                if isinstance(fi_dkz03, list) and fi_dkz03:
                    addr_data = fi_dkz03[0]
                    strasse = addr_data.get('STRASSE', '')
                    hausnummer = addr_data.get('HAUSNUMMER', '')
                    if strasse and hausnummer:
                        address_line = f"{strasse} {hausnummer}"
                    elif strasse:
                        address_line = strasse
                    city = addr_data.get('ORT', '')
            
            # Get legal form from FI_DKZ07
            if 'FI_DKZ07' in firma:
                fi_dkz07 = firma['FI_DKZ07']
                if isinstance(fi_dkz07, list) and fi_dkz07:
                    rechtsform = fi_dkz07[0].get('RECHTSFORM', {})
                    if isinstance(rechtsform, dict):
                        legal_form = rechtsform.get('TEXT', '')
        
        # Extract officers from FUN (Funktionen/Functions)
        officers = []
        if 'FUN' in auszug_data and isinstance(auszug_data['FUN'], list):
            for fun_item in auszug_data['FUN']:
                if isinstance(fun_item, dict):
                    person_nr = fun_item.get('PNR', '')
                    role = fun_item.get('FKENTEXT', 'Officer')
                    
                    # Find person details in PER section
                    person_name = f"Person {person_nr}"
                    if 'PER' in auszug_data and isinstance(auszug_data['PER'], list):
                        for per_item in auszug_data['PER']:
                            if isinstance(per_item, dict) and per_item.get('PNR') == person_nr:
                                # Get person name
                                per_dkz01 = per_item.get('PE_DKZ01', [])
                                if isinstance(per_dkz01, list) and per_dkz01:
                                    name_data = per_dkz01[0]
                                    vorname = name_data.get('VORNAME', '')
                                    nachname = name_data.get('NACHNAME', '')
                                    if vorname and nachname:
                                        person_name = f"{vorname} {nachname}"
                                    elif nachname:
                                        person_name = nachname
                                break
                    
                    officers.append({
                        'company_register_id': register_id,
                        'person_id': person_nr,
                        'person_name': person_name,
                        'role': role,
                        'raw': fun_item
                    })
    
    data = {
        'register_id': register_id,
        'name': name,
        'legal_form': legal_form,
        'status': status,
        'address_line': address_line,
        'city': city,
        'country': 'AT',
        'officers': officers,
        'links': [],
        'raw': auszug_data
    }
    
    return data


def _parse_officers(officers_data, company_register_id: str):
    """
    Parse officer/representative data from various response structures.
    
    Args:
        officers_data: Officer data from API response (can be dict, list, or other)
        company_register_id: The company's register ID
    
    Returns:
        list of officer dicts
    """
    officers = []
    
    if not officers_data:
        return officers
    
    # Handle different data structures
    if isinstance(officers_data, list):
        items = officers_data
    elif isinstance(officers_data, dict):
        items = officers_data.get('items', []) or officers_data.get('PERSON', [])
        if not items:
            items = [officers_data]
    else:
        items = [officers_data]
    
    for item in items:
        if not isinstance(item, dict):
            continue
            
        officer = {
            'company_register_id': company_register_id,
            'person_id': item.get('ID', ''),
            'person_name': item.get('NAME', item.get('name', 'Unknown')),
            'role': item.get('FUNKTION', item.get('rolle', item.get('role', 'Representative'))),
            'raw': item
        }
        officers.append(officer)
    
    return officers


def _insert_into_staging(company_data: dict):
    """
    Insert parsed company data into staging tables.
    
    Args:
        company_data: Structured company data dict
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Insert into stg_companies - use custom JSON encoder for dates
        cur.execute("""
            INSERT INTO stg_companies 
            (register_id, name, legal_form, status, address_line, city, country, raw, src)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (
            company_data['register_id'],
            company_data['name'],
            company_data['legal_form'],
            company_data['status'],
            company_data['address_line'],
            company_data['city'],
            company_data['country'],
            json.dumps(company_data['raw'], cls=DateTimeEncoder),
            'API'
        ))
        
        result = cur.fetchone()
        if result:
            print(f"  ✓ Inserted into stg_companies: {company_data['name']}")
        
        # Insert officers into stg_officers
        for officer in company_data.get('officers', []):
            cur.execute("""
                INSERT INTO stg_officers
                (company_register_id, person_id, person_name, role, raw, src)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                officer['company_register_id'],
                officer['person_id'],
                officer['person_name'],
                officer['role'],
                json.dumps(officer['raw'], cls=DateTimeEncoder),
                'API'
            ))
        
        if company_data.get('officers'):
            print(f"  ✓ Inserted {len(company_data['officers'])} officers into stg_officers")
        
        # Insert links into stg_links (if any)
        for link in company_data.get('links', []):
            cur.execute("""
                INSERT INTO stg_links
                (from_register_id, to_register_id, link_type, raw, src)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                link['from_register_id'],
                link['to_register_id'],
                link['link_type'],
                json.dumps(link.get('raw', {}), cls=DateTimeEncoder),
                'API'
            ))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting into staging: {e}")
        raise
    finally:
        cur.close()
        conn.close()
