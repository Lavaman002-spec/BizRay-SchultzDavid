const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export interface Company {
  id: string;
  register_id: string;
  name: string;
  city: string | null;
  status: string | null;
}

export interface SearchResponse {
  total: number;
  items: Company[];
}

export interface CompanyIdentity {
  id: string;
  register_id: string;
  name: string;
  legal_form: string | null;
  status: string | null;
  address_line: string | null;
  city: string | null;
  country: string | null;
}

export interface Officer {
  person_id: string | null;
  person_name: string;
  role: string;
}

export interface CompanyProfile {
  identity: CompanyIdentity;
  addresses: unknown[];
  officers: Officer[];
  owners: unknown[];
  filings: unknown[];
}

export async function searchCompanies(
  query: string = '',
  limit: number = 20,
  offset: number = 0,
  filters?: { status?: string; city?: string; fetchIfNotFound?: boolean }
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
    offset: offset.toString(),
  });

  if (filters?.status) params.append('status', filters.status);
  if (filters?.city) params.append('city', filters.city);
  if (filters?.fetchIfNotFound) params.append('fetch_if_not_found', 'true');

  const response = await fetch(`${API_BASE_URL}/companies/search?${params}`);

  if (!response.ok) {
    throw new Error('Failed to search companies');
  }

  return response.json();
}

export async function listCompanies(
  limit: number = 12,
  offset: number = 0
): Promise<SearchResponse> {
  // List companies without search query (shows all)
  return searchCompanies('', limit, offset);
}

export async function getCompany(id: string): Promise<CompanyProfile> {
  const response = await fetch(`${API_BASE_URL}/companies/${id}`);

  if (!response.ok) {
    throw new Error('Failed to fetch company');
  }

  return response.json();
}

export async function exportCompanyCSV(id: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/companies/exports/${id}`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Failed to export company');
  }

  return response.blob();
}
