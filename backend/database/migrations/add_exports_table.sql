-- Create exports table for tracking PDF export activity
CREATE TABLE IF NOT EXISTS exports (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    export_type VARCHAR(50) DEFAULT 'pdf',
    exported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for querying exports by company
CREATE INDEX IF NOT EXISTS idx_exports_company_id ON exports(company_id);

-- Create index for querying exports by date
CREATE INDEX IF NOT EXISTS idx_exports_exported_at ON exports(exported_at);

-- Enable Row Level Security
ALTER TABLE exports ENABLE ROW LEVEL SECURITY;

-- Create policies for public access
CREATE POLICY "Enable read access for all users" ON exports FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON exports FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON exports FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON exports FOR DELETE USING (true);
