"""Pydantic models for API request/response validation."""
from __future__ import annotations

from typing import Optional, List, Literal
from datetime import datetime, date as date_type
from pydantic import BaseModel, Field, ConfigDict


# Company Models
class CompanyBase(BaseModel):
    """Base model for company data."""
    fnr: str = Field(..., description="Firmenbuch number (FN)")
    name: str = Field(..., description="Company name")
    legal_form: Optional[str] = None
    state: Optional[str] = Field(None, description="Company state (active, inactive, etc.)")


class CompanyCreate(CompanyBase):
    """Model for creating a new company."""
    pass


class CompanyUpdate(BaseModel):
    fnr: Optional[str] = None
    name: Optional[str] = None
    legal_form: Optional[str] = None
    state: Optional[str] = None


class Company(CompanyBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_fetched_at: Optional[datetime] = None
    city: Optional[str] = Field(default=None, description="Derived primary city from addresses")

    model_config = ConfigDict(from_attributes=True)


# Officer Models (from company_officers table)
class OfficerBase(BaseModel):
    """Base model for officer data."""
    company_id: int = Field(..., description="Company ID this officer belongs to")
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = Field(None, description="Full name of the officer")
    role: Optional[str] = Field(None, description="Role (e.g., GESCHÄFTSFÜHRER)")
    birth_date: Optional[str] = None
    is_active: bool = Field(default=True)
    vnr: Optional[str] = Field(None, description="Version number from Firmenbuch")


class OfficerCreate(OfficerBase):
    """Model for creating a new officer."""
    pass


class OfficerUpdate(BaseModel):
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    birth_date: Optional[str] = None
    is_active: Optional[bool] = None
    vnr: Optional[str] = None


class Officer(OfficerBase):
    """Complete officer model with ID."""
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Address Models (from company_addresses table)
class AddressBase(BaseModel):
    """Base model for address data."""
    company_id: int = Field(..., description="Company ID this address belongs to")
    street: Optional[str] = None
    house_number: Optional[str] = None
    stairway: Optional[str] = None
    door_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, description="Austrian federal state (Bundesland)")
    country: Optional[str] = Field(default="Austria")
    is_deliverable: bool = Field(default=True)
    is_active: bool = Field(default=True)
    vnr: Optional[str] = Field(None, description="Version number from Firmenbuch")


class AddressCreate(AddressBase):
    """Model for creating a new address."""
    pass


class Address(AddressBase):
    """Complete address model with ID."""
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Activity Models (from company_activities table)
class ActivitiesBase(BaseModel):
    """Base model for activities data."""
    company_id: int
    description: str
    is_active: bool = Field(default=True)
    vnr: Optional[str] = None

class Activities(ActivitiesBase):
    """Complete activities model with ID."""
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FinancialBase(BaseModel):
    company_id: int
    year: Optional[int] = None
    revenue: Optional[float] = None
    profit: Optional[float] = None
    currency: Optional[str] = Field(default="EUR")


class Financial(FinancialBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FilingBase(BaseModel):
    company_id: int
    filing_type: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date_type] = None
    status: Optional[str] = None


class Filing(FilingBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RiskBase(BaseModel):
    company_id: int
    risk_type: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date_type] = None
    severity: Optional[str] = None


class Risk(RiskBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CompanyLink(BaseModel):
    id: int
    source_company_id: int
    target_company_id: int
    relationship_type: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RawExtract(BaseModel):
    id: int
    fnr: str
    extract_date: date_type
    extract_type: Optional[str] = None
    raw_data: Optional[dict] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Alert(BaseModel):
    id: int
    user_id: str
    company_id: int
    type: str
    message: str
    is_read: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WatchlistEntry(BaseModel):
    id: int
    user_id: str
    company_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Combined Response Models
class CompanyWithDetails(Company):
    """Company model with associated officers and addresses."""
    officers: List[Officer] = []
    addresses: List[Address] = []
    activities: List[Activities] = []
    financials: List[Financial] = []
    filings: List[Filing] = []
    risks: List[Risk] = []
    links: List[CompanyLink] = []
    raw_extracts: List[RawExtract] = []

    model_config = ConfigDict(from_attributes=True)



class SearchFilters(BaseModel):
    """Filter options for search queries."""

    legal_forms: Optional[List[str]] = Field(
        default=None,
        description="Limit results to companies that match one of the provided legal forms.",
    )
    states: Optional[List[str]] = Field(
        default=None,
        description="Limit results to companies that match one of the provided states.",
    )
    cities: Optional[List[str]] = Field(
        default=None,
        description="Limit results to companies that match one of the provided cities.",
    )


class PaginationParams(BaseModel):
    """Pagination parameters for search queries."""

    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SortParams(BaseModel):
    """Sorting parameters for search queries."""

    field: str = Field(default="name", description="Database column to sort by")
    direction: Literal["asc", "desc"] = Field(default="asc")


class SearchQuery(BaseModel):
    """Model for search requests."""

    q: str = Field(..., min_length=1, description="Search query string")
    filters: Optional[SearchFilters] = Field(
        default=None, description="Optional filters to apply to the search query."
    )
    pagination: PaginationParams = Field(
        default_factory=PaginationParams,
        description="Pagination options for the search query.",
    )
    sort: Optional[SortParams] = Field(
        default=None, description="Optional sorting options for the search query."
    )
    include_relations: bool = Field(
        default=False,
        description="When True, includes officers and addresses with each company.",
    )


class SearchResponse(BaseModel):
    """Model for search results."""

    total: int = Field(..., description="Total number of matching companies.")
    count: int = Field(..., description="Number of companies returned in this response.")
    results: List[CompanyWithDetails]
    limit: int = Field(..., description="Limit that was used when fetching the results.")
    offset: int = Field(..., description="Offset that was used when fetching the results.")
    next_offset: Optional[int] = Field(
        default=None,
        description="Offset for the next page of results, if there are more results.",
    )
    has_more: bool = Field(
        default=False, description="Whether additional pages of results are available."
    )


class SearchSuggestion(BaseModel):
    """Individual search suggestion entry."""

    name: str = Field(..., description="Suggested company name")
    fnr: Optional[str] = Field(
        default=None, description="Firmenbuch number associated with the suggestion"
    )


class SearchSuggestionsResponse(BaseModel):
    """Response model for autocomplete suggestions."""

    query: str
    suggestions: List[SearchSuggestion] = Field(default_factory=list)


# Export Models
class ExportBase(BaseModel):
    """Base model for export data."""
    company_id: int = Field(..., description="Company ID for the export")
    export_type: str = Field(default="pdf", description="Type of export (pdf, json, etc.)")


class ExportCreate(ExportBase):
    """Model for creating a new export record."""
    pass


class Export(ExportBase):
    """Complete export model with ID."""
    id: int
    exported_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Health Check Model
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    database: str
    
    
class DashboardStats(BaseModel):
    total_companies: int
    active_companies: int
    total_officers: int