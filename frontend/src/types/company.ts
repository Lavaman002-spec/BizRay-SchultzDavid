// API Types matching backend schema
export interface Company {
  id: number;
  fnr: string;
  name: string;
  legal_form: string | null;
  state: string | null;
  city: string | null;
  created_at: string | null;
  updated_at: string | null;
  last_fetched_at: string | null;
  revenue?: number | null;
  profit?: number | null;
  latest_financial_year?: number | null;
  revenue_currency?: string | null;
  // Optional address for search results
  address?: Address;
}

export interface Officer {
  id: number;
  company_id: number;
  title: string | null;
  first_name: string | null;
  last_name: string | null;
  full_name: string | null;
  role: string | null;
  birth_date: string | null;
  is_active: boolean;
  vnr: string | null;
  created_at: string | null;
}

export interface Address {
  id: number;
  company_id: number;
  street: string | null;
  house_number: string | null;
  stairway: string | null;
  door_number: string | null;
  postal_code: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  is_deliverable: boolean;
  is_active: boolean;
  vnr: string | null;
  created_at: string | null;
}

export interface Activities {
  id: number;
  company_id: number;
  description: string;
  is_active: boolean;
  vnr: string | null;
  created_at: string | null;
}

export interface Financials {
  id: number;
  company_id: number;
  year: number;
  revenue: number | null;
  profit: number | null;
  currency: string | null;
  created_at: string | null;
}

export interface Filing {
  id: number;
  company_id: number;
  filing_type: string | null;
  description: string | null;
  date: string | null;
  status: string | null;
  created_at: string | null;
}

export interface Risk {
  id: number;
  company_id: number;
  risk_type: string | null;
  description: string | null;
  date: string | null;
  severity: string | null;
  created_at: string | null;
}

export interface CompanyLink {
  id: number;
  source_company_id: number;
  target_company_id: number;
  relationship_type: string | null;
  created_at: string | null;
}

export interface RawExtract {
  id: number;
  fnr: string;
  extract_date: string;
  extract_type: string | null;
  raw_data: Record<string, unknown> | string | null;
  created_at: string | null;
}

export interface CompanyWithDetails extends Company {
  officers: Officer[];
  addresses: Address[];
  activities: Activities[];
  financials: Financials[];
  filings: Filing[];
  risks: Risk[];
  links?: CompanyLink[];
  raw_extracts?: RawExtract[];
}

export interface WatchlistEntry {
  id: number;
  user_id: string;
  company_id: number;
  created_at: string | null;
  notify_via_email?: boolean | null;
  last_notified_at?: string | null;
  last_change_digest?: string | null;
  company?: CompanyWithDetails | null;
}

export interface SearchFilters {
  legal_forms?: string[];
  states?: string[];
  cities?: string[];
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

export type SortDirection = 'asc' | 'desc';

export interface SortParams {
  field?: string;
  direction?: SortDirection;
}

export interface SearchQuery {
  q: string;
  filters?: SearchFilters;
  pagination?: PaginationParams;
  sort?: SortParams;
  include_relations?: boolean;
}

export interface SearchResponse {
  total: number;
  count: number;
  results: CompanyWithDetails[];
  limit: number;
  offset: number;
  next_offset?: number | null;
  has_more: boolean;
}

export interface SearchSuggestion {
  name: string;
  fnr?: string | null;
}

export interface SearchSuggestionsResponse {
  query: string;
  suggestions: SearchSuggestion[];
}

export interface HealthCheck {
  status: string;
  timestamp: string;
  database: string;
}

// Legacy interface for backward compatibility
export interface CompanyItem {
  id: string;
  register_id?: string;
  name?: string;
  city?: string;
  status?: string;
  legal_form?: string;
}
