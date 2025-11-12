import type {
  Company,
  CompanyWithDetails,
  SearchQuery,
  SearchResponse,
  SearchSuggestionsResponse,
  HealthCheck,
  Officer,
} from '@/types/company';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function to handle API responses
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }
  return response.json();
}

// Locations endpoints
export async function getCities(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/locations/cities`);
  return handleResponse<string[]>(response);
}

// Health check endpoint
export async function checkHealth(): Promise<HealthCheck> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleResponse<HealthCheck>(response);
}

// Search companies by name or FNR
export async function searchCompanies(
  query: string,
  limit: number = 50,
  offset: number = 0,
  city?: string
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    query,
    limit: limit.toString(),
    offset: offset.toString(),
  });

  // Add city parameter if provided
  if (city) {
    params.append('city', city);
  }

  const response = await fetch(`${API_BASE_URL}/api/search/?${params}`);
  return handleResponse<SearchResponse>(response);
}

/**
 * Perform an advanced company search with filters and sorting
 */
export async function advancedSearchCompanies(
  payload: SearchQuery
): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/search/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse<SearchResponse>(response);
}

/**
 * Fetch autocomplete suggestions for a search query
 */
export async function getSearchSuggestions(
  query: string,
  limit: number = 10
): Promise<SearchSuggestionsResponse> {
  const params = new URLSearchParams({
    query,
    limit: limit.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/api/search/suggest?${params}`);
  return handleResponse<SearchSuggestionsResponse>(response);
}

/**
 * Convenience wrapper returning just company name suggestions as strings
 */
export async function getCompanySuggestions(
  query: string,
  limit: number = 10
): Promise<string[]> {
  const params = new URLSearchParams({
    query,
    limit: limit.toString(),
  });
  const response = await fetch(`${API_BASE_URL}/api/search/suggest?${params}`);
  const data = await handleResponse<SearchSuggestionsResponse>(response);
  return data.suggestions.map((s) => s.name);
}

/**
 * Get all companies with pagination
 */
export async function listCompanies(
  limit: number = 100,
  offset: number = 0
): Promise<CompanyWithDetails[]> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/api/companies/?${params}`);
  return handleResponse<CompanyWithDetails[]>(response);
}

// Get a specific company by ID with officers and addresses
export async function getCompany(id: number): Promise<CompanyWithDetails> {
  const response = await fetch(`${API_BASE_URL}/api/companies/${id}`);
  return handleResponse<CompanyWithDetails>(response);
}

// Get a company by Firmenbuch number (FNR)
export async function getCompanyByFnr(fnr: string): Promise<Company> {
  const response = await fetch(`${API_BASE_URL}/api/companies/fnr/${fnr}`);
  return handleResponse<Company>(response);
}

// Create a new company
export async function createCompany(data: {
  fnr: string;
  name: string;
  legal_form?: string;
  state?: string;
  city?: string;
}): Promise<Company> {
  const response = await fetch(`${API_BASE_URL}/api/companies/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<Company>(response);
}

// Update a company
export async function updateCompany(
  id: number,
  data: Partial<{
    fnr: string;
    name: string;
    legal_form: string;
    state: string;
    city: string;
  }>
): Promise<Company> {
  const response = await fetch(`${API_BASE_URL}/api/companies/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<Company>(response);
}

//Delete a company
export async function deleteCompany(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/companies/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete company');
  }
}

//Get all officers with pagination
export async function listOfficers(
  limit: number = 100,
  offset: number = 0
): Promise<Officer[]> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/api/officers/?${params}`);
  return handleResponse<Officer[]>(response);
}

//Get officers by company ID
export async function getOfficersByCompany(
  companyId: number
): Promise<Officer[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/officers/company/${companyId}`
  );
  return handleResponse<Officer[]>(response);
}

//Get a specific officer by ID
export async function getOfficer(id: number): Promise<Officer> {
  const response = await fetch(`${API_BASE_URL}/api/officers/${id}`);
  return handleResponse<Officer>(response);
}

//Create a new officer
export async function createOfficer(data: {
  company_id: number;
  title?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  role?: string;
  birth_date?: string;
  is_active?: boolean;
  vnr?: string;
}): Promise<Officer> {
  const response = await fetch(`${API_BASE_URL}/api/officers/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<Officer>(response);
}

export type {
  Company,
  CompanyWithDetails,
  SearchResponse,
  HealthCheck,
  Officer,
};
