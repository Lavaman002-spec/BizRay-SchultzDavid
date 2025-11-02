-- BizRay Database Schema
-- Austrian Business Register (Firmenbuch) Database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies Table
CREATE TABLE IF NOT EXISTS company_addresses (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    street TEXT,
    house_number TEXT,
    stairway TEXT,
    door_number TEXT,
    postal_code TEXT,
    city TEXT,
    country TEXT,
    is_deliverable BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    vnr TEXT,  -- Version number from API
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_addresses_company_id ON company_addresses(company_id);


-- Officers Table
CREATE TABLE IF NOT EXISTS company_officers (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    title TEXT,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    role TEXT,  -- Geschäftsführer, etc.
    birth_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    vnr TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_officers_company_id ON company_officers(company_id);
CREATE INDEX idx_officers_name ON company_officers(full_name);

-- Company-Officer Junction Table
CREATE TABLE IF NOT EXISTS company_officers (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    officer_id INTEGER NOT NULL REFERENCES officers(id) ON DELETE CASCADE,
    role VARCHAR(100),
    appointed_date VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, officer_id)
);

-- Company Links/Relationships Table
CREATE TABLE IF NOT EXISTS links (
    id SERIAL PRIMARY KEY,
    source_company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    target_company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_company_id, target_company_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_companies_fn_number ON companies(fn_number);
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_city ON companies(city);
CREATE INDEX IF NOT EXISTS idx_officers_last_name ON officers(last_name);
CREATE INDEX IF NOT EXISTS idx_company_officers_company_id ON company_officers(company_id);
CREATE INDEX IF NOT EXISTS idx_company_officers_officer_id ON company_officers(officer_id);
CREATE INDEX IF NOT EXISTS idx_links_source_company_id ON links(source_company_id);
CREATE INDEX IF NOT EXISTS idx_links_target_company_id ON links(target_company_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_companies_updated_at 
    BEFORE UPDATE ON companies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (optional, but recommended for Supabase)
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE officers ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_officers ENABLE ROW LEVEL SECURITY;
ALTER TABLE links ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust based on your security requirements)
CREATE POLICY "Enable read access for all users" ON companies FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON companies FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON companies FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON companies FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON officers FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON officers FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON officers FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON officers FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON company_officers FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON company_officers FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON company_officers FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON company_officers FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON links FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON links FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON links FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON links FOR DELETE USING (true);
