import sys
import os

# Load environment first
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

from zeep import Client
from zeep.transports import Transport
from zeep.helpers import serialize_object
from requests import Session
from datetime import date
import json

API_KEY = os.getenv("API_KEY")
WSDL_URL = os.getenv("WSDL_URL", "https://justizonline.gv.at/jop/api/at.gv.justiz.fbw/ws?wsdl")

def create_client():
    """Create SOAP client."""
    session = Session()
    session.headers.update({
        'X-API-KEY': f'{API_KEY}', 
        'Content-Type': 'application/soap+xml;charset=UTF-8'
    })
    transport = Transport(session=session)
    client = Client(wsdl=WSDL_URL, transport=transport)
    
    for service in client.wsdl.services.values():
        for port in service.ports.values():
            port.binding_options['address'] = "https://justizonline.gv.at/jop/api/at.gv.justiz.fbw/ws"
    
    return client

def auszug_v2(fnr: str, umfang: str = "Kurzinformation"):
    """Request AUSZUG_V2_ (company extract) for the given FNR."""
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

# Fetch company data
fnr = "348406m"
print(f"Fetching data for {fnr}...")
data = auszug_v2(fnr)

if data:
    print("\n=== Top-level keys ===")
    if isinstance(data, dict):
        for key in sorted(data.keys()):
            value = data[key]
            if isinstance(value, list):
                print(f"  - {key}: list with {len(value)} items")
            elif isinstance(value, dict):
                print(f"  - {key}: dict")
            else:
                print(f"  - {key}: {type(value).__name__}")
    
    # Save full output to file for inspection
    with open('/tmp/auszug_full.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print("\n=== FI_DKZ02 (Company Name) ===")
    if 'FI_DKZ02' in data:
        print(json.dumps(data['FI_DKZ02'], indent=2, default=str))
    else:
        print("Not found")
    
    print("\n=== Searching for name-related fields ===")
    for key in sorted(data.keys()):
        key_upper = key.upper()
        if 'FIRMA' in key_upper or 'NAME' in key_upper or 'BEZEICH' in key_upper:
            print(f"\nFound: {key}")
            val_str = json.dumps(data[key], indent=2, default=str)
            print(val_str[:500] if len(val_str) > 500 else val_str)
    
    print("\n✓ Full data saved to /tmp/auszug_full.json")
    print("You can view it with: cat /tmp/auszug_full.json | less")
else:
    print("No data received!")