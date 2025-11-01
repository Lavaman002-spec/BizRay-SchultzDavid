CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- STAGING
CREATE TABLE IF NOT EXISTS stg_companies (
  id BIGSERIAL PRIMARY KEY,
  register_id TEXT,
  name TEXT,
  legal_form TEXT,
  status TEXT,
  address_line TEXT,
  city TEXT,
  country TEXT,
  raw JSONB,
  src TEXT,
  ingested_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stg_officers (
  id BIGSERIAL PRIMARY KEY,
  company_register_id TEXT,
  person_id TEXT,
  person_name TEXT,
  role TEXT,
  raw JSONB,
  src TEXT,
  ingested_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stg_links (
  id BIGSERIAL PRIMARY KEY,
  from_register_id TEXT,
  to_register_id TEXT,
  link_type TEXT,
  raw JSONB,
  src TEXT,
  ingested_at TIMESTAMPTZ DEFAULT now()
);

-- CANONICAL
CREATE TABLE IF NOT EXISTS companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  canonical_key TEXT UNIQUE,
  register_id TEXT,
  name TEXT,
  legal_form TEXT,
  status TEXT,
  address_line TEXT,
  city TEXT,
  country TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_companies_name_trgm ON companies USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_companies_register ON companies (register_id);

CREATE TABLE IF NOT EXISTS officers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  person_id TEXT,
  person_name TEXT,
  role TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ownership_links (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  from_company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  to_company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  link_type TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);