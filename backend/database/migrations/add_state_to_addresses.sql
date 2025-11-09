-- Add state column to company_addresses table
-- This represents the Austrian federal state (Bundesland)

-- Step 1: Add the state column
DO $$
BEGIN
    -- Check if column exists, if not add it
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'company_addresses'
        AND column_name = 'state'
    ) THEN∑
        ALTER TABLE company_addresses ADD COLUMN state TEXT;
    END IF;
END $$;

-- Step 2: Create index for better query performance on state filtering
CREATE INDEX IF NOT EXISTS idx_addresses_state ON company_addresses(state);

-- Step 3: Update existing rows to set state based on city if needed
-- Example updates for major cities:
UPDATE company_addresses SET state = 'Wien' WHERE (city ILIKE '%Wien%' OR city ILIKE '%Vienna%') AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Salzburg' WHERE city ILIKE '%Salzburg%' AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Tirol' WHERE city ILIKE '%Innsbruck%' AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Steiermark' WHERE city ILIKE '%Graz%' AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Oberösterreich' WHERE (city ILIKE '%Linz%' OR city ILIKE '%Wels%' OR city ILIKE '%Steyr%') AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Kärnten' WHERE (city ILIKE '%Klagenfurt%' OR city ILIKE '%Villach%') AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Niederösterreich' WHERE (city ILIKE '%Sankt Pölten%' OR city ILIKE '%Wiener Neustadt%') AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Vorarlberg' WHERE (city ILIKE '%Dornbirn%' OR city ILIKE '%Bregenz%' OR city ILIKE '%Feldkirch%') AND (state IS NULL OR state = '');
