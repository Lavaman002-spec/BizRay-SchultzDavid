# proxy.py
from datetime import date
import os
import requests
import zeep
from zeep import Client, Settings, Transport

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── ENV ────────────────────────────────────────────────────────────────────────
load_dotenv()  # loads backend/.env
API_KEY = os.getenv("API_KEY")
WSDL_URL = os.getenv("WSDL_URL")

if not API_KEY or not WSDL_URL:
    raise RuntimeError("Set API_KEY and WSDL_URL in registry-proxy/.env")

# ── APP ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="BizRay Registry Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SOAP CLIENT CACHE ──────────────────────────────────────────────────────────
_cached_client = None
_client_error = None


def make_client() -> Client:
    """
    Build a Zeep client that can download the WSDL with the API key header.
    If anything fails, raise HTTPException with a clear message.
    """
    global _cached_client, _client_error

    # Return cached client if available
    if _cached_client is not None:
        print("[make_client] Using cached client")
        return _cached_client

    # If we previously failed, raise that error
    if _client_error is not None:
        print(f"[make_client] Returning cached error: {_client_error}")
        raise HTTPException(status_code=502, detail=str(_client_error))

    try:
        print(f"[make_client] Loading WSDL from {WSDL_URL}")
        print(f"[make_client] API Key (first 10 chars): {API_KEY[:10]}...")

        # Create session with API key
        session = requests.Session()
        session.headers.update({
            "X-API-KEY": API_KEY,
        })

        # Test if we can reach the WSDL URL first
        print("[make_client] Testing WSDL URL accessibility...")
        test_response = session.get(WSDL_URL, timeout=10)
        print(f"[make_client] WSDL URL response status: {test_response.status_code}")

        if test_response.status_code != 200:
            error_msg = f"WSDL URL returned status {test_response.status_code}: {test_response.text[:200]}"
            print(f"[make_client] {error_msg}")
            _client_error = error_msg
            raise HTTPException(status_code=502, detail=error_msg)

        # Create transport and settings
        transport = Transport(session=session, timeout=60)
        settings = Settings(strict=False, xml_huge_tree=True)

        # Create client
        print("[make_client] Creating Zeep client...")
        client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

        print("[make_client] WSDL loaded successfully")
        print(f"[make_client] Available services: {[s.name for s in client.wsdl.services.values()]}")

        # Override the service endpoint to use public domain instead of internal
        # The WSDL references fbw.justiz.intra.gv.at (internal), but we need justizonline.gv.at (public)
        for service in client.wsdl.services.values():
            for port in service.ports.values():
                old_location = port.binding_options.get('address')
                if old_location and 'intra.gv.at' in old_location:
                    # Replace internal domain with public domain and ensure we use the JOP API path
                    new_location = old_location.replace(
                        'https://fbw.justiz.intra.gv.at/at.gv.justiz.fbw/ws',
                        'https://justizonline.gv.at/jop/api/at.gv.justiz.fbw/ws'
                    )
                    port.binding_options['address'] = new_location
                    print(f"[make_client] Overriding endpoint: {old_location} -> {new_location}")

        # Cache the client
        _cached_client = client

        return client

    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error loading WSDL: {type(e).__name__}: {str(e)}"
        print(f"[make_client] {error_msg}")
        import traceback
        traceback.print_exc()
        _client_error = error_msg
        raise HTTPException(status_code=502, detail=error_msg)
    except Exception as e:
        error_msg = f"WSDL load failed: {type(e).__name__}: {str(e)}"
        print(f"[make_client] {error_msg}")
        import traceback
        traceback.print_exc()
        _client_error = error_msg
        raise HTTPException(status_code=502, detail=error_msg)


# ── DIAGNOSTICS ────────────────────────────────────────────────────────────────
@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/debug")
def debug():
    """Enhanced debug endpoint"""
    debug_info = {
        "has_api_key": bool(API_KEY),
        "api_key_length": len(API_KEY) if API_KEY else 0,
        "api_key_preview": API_KEY[:10] + "..." if API_KEY else None,
        "wsdl_url": WSDL_URL,
        "client_cached": _cached_client is not None,
        "client_error": str(_client_error) if _client_error else None
    }

    # Try to create client if not cached
    if not _cached_client and not _client_error:
        try:
            client = make_client()
            debug_info["client_creation"] = "success"
            debug_info["services"] = [s.name for s in client.wsdl.services.values()]
        except Exception as e:
            debug_info["client_creation"] = "failed"
            debug_info["client_creation_error"] = str(e)

    return debug_info


@app.get("/test-wsdl")
def test_wsdl():
    """Test WSDL accessibility"""
    session = requests.Session()
    session.headers.update({"X-API-KEY": API_KEY})

    try:
        response = session.get(WSDL_URL, timeout=10)
        return {
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type"),
            "content_length": len(response.content),
            "content_preview": response.text[:500]
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }


@app.get("/inspect-endpoints")
def inspect_endpoints():
    """Inspect SOAP service endpoints from WSDL"""
    try:
        client = make_client()

        endpoints = {}
        for service in client.wsdl.services.values():
            endpoints[service.name] = {}
            for port in service.ports.values():
                endpoints[service.name][port.name] = {
                    "binding": str(port.binding),
                    "location": port.binding_options.get('address')
                }

        return {
            "endpoints": endpoints,
            "note": "If location shows 'intra.gv.at', the service is internal-only"
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }


@app.get("/test-soap-endpoint")
def test_soap_endpoint():
    """Test what the SOAP endpoint returns"""
    try:
        client = make_client()

        # Get the endpoint URL
        service = list(client.wsdl.services.values())[0]
        port = list(service.ports.values())[0]
        endpoint_url = port.binding_options.get('address')

        # Try to POST a simple request
        session = requests.Session()
        session.headers.update({"X-API-KEY": API_KEY})

        response = session.get(endpoint_url, timeout=10)

        return {
            "endpoint_url": endpoint_url,
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type"),
            "response_preview": response.text[:1000]
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


# ── ROUTES ─────────────────────────────────────────────────────────────────────
@app.get("/search")
def search(q: str = Query(..., min_length=2)):
    try:
        client = make_client()

        print(f"[/search] Searching for: {q}")

        args = dict(
            FIRMENWORTLAUT=q,
            EXAKTESUCHE=False,
            SUCHBEREICH=1,
            GERICHT="",
            RECHTSFORM="",
            RECHTSEIGENSCHAFT="",
            ORTNR=""
        )

        resp = client.service.SUCHEFIRMA(**args)

        items = []
        for e in (getattr(resp, "ERGEBNIS", None) or []):
            items.append({
                "fnr": getattr(e, "FNR", None),
                "name": (getattr(e, "NAME", None) or [None])[0],
            })

        print(f"[/search] Found {len(items)} results")
        return JSONResponse({"results": items})

    except HTTPException:
        raise
    except Exception as ex:
        print(f"[/search] SOAP call failed: {type(ex).__name__}: {str(ex)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"Search failed: {ex}")


@app.get("/company/{fnr}")
def company(fnr: str):
    try:
        client = make_client()

        print(f"[/company] Fetching company: {fnr}")

        today = date.today().isoformat()
        resp = client.service.AUSZUG_V2_(FNR=fnr, STICHTAG=today, UMFANG="Kurzinformation")

        return JSONResponse(zeep.helpers.serialize_object(resp, target_cls=dict))

    except HTTPException:
        raise
    except Exception as ex:
        print(f"[/company] SOAP call failed: {type(ex).__name__}: {str(ex)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"Company failed: {ex}")

print("scrum 2")