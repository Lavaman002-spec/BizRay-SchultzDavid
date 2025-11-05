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
  country: string | null;
  is_deliverable: boolean;
  is_active: boolean;
  vnr: string | null;
  created_at: string | null;
}

export interface CompanyWithDetails extends Company {
  officers: Officer[];
  addresses: Address[];
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
