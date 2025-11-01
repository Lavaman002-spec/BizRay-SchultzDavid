from pydantic import BaseModel
from typing import List, Optional

class CompanyIdentity(BaseModel):
    id: str
    register_id: str
    name: str
    legal_form: Optional[str] = None
    status: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class Officer(BaseModel):
    person_id: Optional[str] = None
    person_name: str
    role: str

class CompanyProfile(BaseModel):
    identity: CompanyIdentity
    addresses: List = []
    officers: List[Officer] = []
    owners: List = []
    filings: List = []

class SearchResultItem(BaseModel):
    id: str
    register_id: str
    name: str
    city: Optional[str] = None
    status: Optional[str] = None

class SearchResponse(BaseModel):
    total: int
    items: List[SearchResultItem]