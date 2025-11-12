-- Add indexes for faster text search on companies table
-- These indexes will significantly improve ILIKE query performance

-- Enable pg_trgm extension for trigram-based text search (better for ILIKE with %)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Drop old indexes if they exist
DROP INDEX IF EXISTS idx_companies_fn_number;
DROP INDEX IF EXISTS idx_companies_name;

-- Create GIN indexes using pg_trgm for fast ILIKE queries
CREATE INDEX IF NOT EXISTS idx_companies_name_trgm ON companies USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_companies_fnr_trgm ON companies USING GIN (fnr gin_trgm_ops);

-- Add standard B-tree indexes for exact matches and sorting
CREATE INDEX IF NOT EXISTS idx_companies_fnr ON companies(fnr);
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_city ON companies(city);
CREATE INDEX IF NOT EXISTS idx_companies_state ON companies(state);

-- Add indexes for company_id lookups in related tables
CREATE INDEX IF NOT EXISTS idx_company_addresses_company_id ON company_addresses(company_id);
CREATE INDEX IF NOT EXISTS idx_company_officers_company_id ON company_officers(company_id);
CREATE INDEX IF NOT EXISTS idx_company_activities_company_id ON company_activities(company_id);
