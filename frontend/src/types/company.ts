// API Types matching backend schema
export interface Company {
  id: number;
  fnr: string;
  name: string;
  legal_form: string | null;
  state: string | null;
  created_at: string | null;
  updated_at: string | null;
  last_fetched_at: string | null;
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

export interface CompanyWithDetails extends Company {
  officers: Officer[];
  addresses: Address[];
}

export interface SearchResponse {
  total: number;
  results: Company[];
  limit: number;
  offset: number;
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
