"""Client for interacting with the Austrian Firmenbuch SOAP API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging
from typing import Any, Dict, List, Optional

from zeep import Client as ZeepClient
from zeep.transports import Transport
from zeep.exceptions import Fault as ZeepFault
from zeep.helpers import serialize_object
from requests import Session

from backend.shared.config import API_KEY, WSDL_URL

logger = logging.getLogger(__name__)


class FirmenbuchAPIError(Exception):
    """Raised when the Firmenbuch API returns an error response."""


@dataclass
class FirmenbuchAPIClient:
    """SOAP client for the Austrian Firmenbuch API."""

    wsdl_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 30
    _client: Optional[ZeepClient] = None

    def __post_init__(self) -> None:
        self.wsdl_url = self.wsdl_url or WSDL_URL
        self.api_key = self.api_key or API_KEY

        if not self.wsdl_url:
            raise ValueError(
                "WSDL_URL environment variable must be configured to "
                "use the Firmenbuch API client."
            )

        if not self.api_key:
            raise ValueError(
                "API_KEY environment variable must be configured to "
                "use the Firmenbuch API client."
            )

    def _get_client(self) -> ZeepClient:
        """Lazy initialize and return the SOAP client."""
        if self._client is None:
            session = Session()
            session.headers.update({
                'X-API-KEY': f'{self.api_key}',
                'Content-Type': 'application/soap+xml;charset=UTF-8'
            })
            transport = Transport(session=session, timeout=self.timeout)
            self._client = ZeepClient(wsdl=self.wsdl_url, transport=transport)

            # Set the correct service endpoint
            for service in self._client.wsdl.services.values():
                for port in service.ports.values():
                    port.binding_options['address'] = "https://justizonline.gv.at/jop/api/at.gv.justiz.fbw/ws"

        return self._client

    # -- Public API -----------------------------------------------------
    def get_company_profile(self, register_id: str) -> Optional[Dict[str, Any]]:
        """Return the company profile for the given Firmenbuch number."""

        if not register_id:
            raise ValueError("register_id must be provided")

        logger.debug("Requesting Firmenbuch profile %s via SOAP", register_id)

        try:
            client = self._get_client()

            # Call AUSZUG_V2_ to get company details
            response = client.service.AUSZUG_V2_(
                FNR=register_id,
                STICHTAG=date.today().isoformat(),
                UMFANG="Kurzinformation"
            )

            if not response:
                logger.info("Firmenbuch record %s not found", register_id)
                return None

            # Convert SOAP response to dictionary format
            payload = self._convert_auszug_to_dict(response, register_id)

            logger.info("Successfully fetched Firmenbuch profile for %s", register_id)
            return payload

        except ZeepFault as exc:
            logger.warning("SOAP fault for %s: %s", register_id, exc.message)
            return None
        except Exception as exc:
            logger.exception("Failed to fetch Firmenbuch profile %s", register_id)
            raise FirmenbuchAPIError(f"Connection to Firmenbuch API failed: {exc}") from exc

    def search_companies(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Return Firmenbuch search matches for the provided query string."""

        query = (query or "").strip()
        if not query:
            raise ValueError("query must be provided")

        logger.debug("Searching Firmenbuch for '%s' via SOAP", query)

        try:
            client = self._get_client()

            # Call SUCHEFIRMA to search for companies
            response = client.service.SUCHEFIRMA(
                FIRMENWORTLAUT=query,
                EXAKTESUCHE=False,
                SUCHBEREICH=1,
                GERICHT="",
                RECHTSFORM="",
                RECHTSEIGENSCHAFT="",
                ORTNR=""
            )

            if not response or not hasattr(response, 'ERGEBNIS'):
                logger.info("No Firmenbuch matches found for '%s'", query)
                return []

            results = []
            for ergebnis in response.ERGEBNIS[:limit]:
                # Extract company name (can be a list or string)
                name = ergebnis.NAME
                if isinstance(name, list) and name:
                    name = name[0]

                result = {
                    "fnr": ergebnis.FNR,
                    "name": str(name) if name else None,
                    "companyName": str(name) if name else None,
                }
                results.append(result)

            logger.info("Found %d Firmenbuch matches for '%s'", len(results), query)
            return results

        except ZeepFault as exc:
            logger.warning("SOAP fault searching for '%s': %s", query, exc.message)
            return []
        except Exception as exc:
            logger.exception("Failed to search Firmenbuch for '%s'", query)
            raise FirmenbuchAPIError(f"Connection to Firmenbuch API failed: {exc}") from exc

    # -- Internal helpers -----------------------------------------------
    def _convert_auszug_to_dict(self, response: Any, fnr: str) -> Dict[str, Any]:
        """Convert SOAP AUSZUG response to dictionary format."""

        payload = {
            "company": {
                "fnr": fnr,
                "name": None,
                "legalForm": None,
                "status": "Active",
                "addresses": [],
                "officers": [],
                "activities": []
            }
        }

        try:
            # Extract company name from FIRMA.FI_DKZ02 (company name designation)
            if hasattr(response, 'FIRMA') and response.FIRMA:
                firma = response.FIRMA
                logger.debug("FIRMA object found for %s", fnr)

                # Company name from FI_DKZ02
                fi_dkz02 = getattr(firma, 'FI_DKZ02', None)
                if fi_dkz02:
                    for zeep_entry in fi_dkz02:
                        # Convert Zeep object to dictionary
                        entry = serialize_object(zeep_entry) if hasattr(zeep_entry, '__dict__') else zeep_entry
                        if isinstance(entry, dict):
                            if entry.get('AUFRECHT') and 'BEZEICHNUNG' in entry and entry['BEZEICHNUNG']:
                                name = entry['BEZEICHNUNG']
                                if isinstance(name, list) and name:
                                    payload["company"]["name"] = str(name[0])
                                    logger.info("Extracted company name for %s: %s", fnr, payload["company"]["name"])
                                else:
                                    payload["company"]["name"] = str(name)
                                    logger.info("Extracted company name for %s: %s", fnr, payload["company"]["name"])
                                break
                else:
                    logger.warning("No FI_DKZ02 found for %s", fnr)

                # Location/registered office from FI_DKZ06
                fi_dkz06 = getattr(firma, 'FI_DKZ06', None)
                if fi_dkz06:
                    for zeep_entry in fi_dkz06:
                        # Convert Zeep object to dictionary
                        entry = serialize_object(zeep_entry) if hasattr(zeep_entry, '__dict__') else zeep_entry
                        if isinstance(entry, dict):
                            if entry.get('AUFRECHT') and 'SITZ' in entry:
                                city = str(entry['SITZ']) if entry['SITZ'] else None
                                if city:
                                    payload["company"]["addresses"].append({
                                        "city": city,
                                        "country": "Austria"
                                    })
                                break

            # Extract persons from PER (officers/directors)
            if hasattr(response, 'PER') and response.PER:
                for person_entry in response.PER:
                    if isinstance(person_entry, dict):
                        # Extract name from various possible fields
                        full_name = None
                        role = None

                        # Try to get person details from nested structure
                        if 'PE_PERS' in person_entry:
                            pe_pers = person_entry['PE_PERS']
                            if isinstance(pe_pers, list) and pe_pers:
                                pe_pers = pe_pers[0]
                            if isinstance(pe_pers, dict):
                                # Name might be in NACHNAME/VORNAME or BEZEICHNUNG
                                vorname = pe_pers.get('VORNAME', '')
                                nachname = pe_pers.get('NACHNAME', '')
                                if vorname or nachname:
                                    full_name = f"{vorname} {nachname}".strip()
                                elif 'BEZEICHNUNG' in pe_pers and pe_pers['BEZEICHNUNG']:
                                    bezeichnung = pe_pers['BEZEICHNUNG']
                                    if isinstance(bezeichnung, list) and bezeichnung:
                                        full_name = str(bezeichnung[0])
                                    else:
                                        full_name = str(bezeichnung)

                        # Try to get role from PE_FUN (function)
                        if 'PE_FUN' in person_entry and person_entry['PE_FUN']:
                            pe_fun = person_entry['PE_FUN']
                            if isinstance(pe_fun, list) and pe_fun:
                                pe_fun = pe_fun[0]
                            if isinstance(pe_fun, dict) and 'FUNTXT' in pe_fun:
                                funtxt = pe_fun['FUNTXT']
                                if isinstance(funtxt, list) and funtxt:
                                    role = str(funtxt[0])
                                else:
                                    role = str(funtxt) if funtxt else None

                        if full_name:
                            payload["company"]["officers"].append({
                                "fullName": full_name,
                                "role": role
                            })

            # Try to determine legal form from company name
            if payload["company"]["name"]:
                name = payload["company"]["name"]
                if " GmbH" in name:
                    payload["company"]["legalForm"] = "GmbH"
                elif " AG" in name:
                    payload["company"]["legalForm"] = "AG"
                elif " KG" in name:
                    payload["company"]["legalForm"] = "KG"
                elif " OG" in name:
                    payload["company"]["legalForm"] = "OG"

        except Exception as exc:
            logger.warning("Error parsing AUSZUG response for %s: %s", fnr, exc)
            logger.exception("Full exception details:")

        return payload


__all__ = [
    "FirmenbuchAPIClient",
    "FirmenbuchAPIError",
]

