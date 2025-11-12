# Database Migrations

This directory contains SQL migration files for the BizRay database schema.

## How to Apply Migrations

### Option 1: Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Create a new query
4. Copy and paste the contents of the migration file
5. Click **Run** to execute the migration

### Option 2: Using Supabase CLI

```bash
supabase db push
```

## Current Migrations

### `add_state_to_addresses.sql`

**Purpose**: Adds the `state` column to the `company_addresses` table to support filtering by Austrian federal states (Bundesländer).

**Required for**: Location-based search filtering by state

**To apply this migration:**
1. Open your Supabase SQL Editor: https://app.supabase.com/project/YOUR_PROJECT_ID/sql
2. Copy the contents of `add_state_to_addresses.sql`
3. Paste and run in the SQL Editor

**What it does:**
- Adds `state TEXT` column to `company_addresses`
- Creates an index on the `state` column for better query performance
- Updates existing records to populate state based on city names

## Quick Copy-Paste SQL (For add_state_to_addresses.sql)

If you're getting errors, copy and paste this complete SQL into your Supabase SQL Editor:

```sql
-- Step 1: Add the state column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'company_addresses'
        AND column_name = 'state'
    ) THEN
        ALTER TABLE company_addresses ADD COLUMN state TEXT;
    END IF;
END $$;

-- Step 2: Create index
CREATE INDEX IF NOT EXISTS idx_addresses_state ON company_addresses(state);

-- Step 3: Update existing rows based on city
UPDATE company_addresses SET state = 'Wien' WHERE (city ILIKE '%Wien%' OR city ILIKE '%Vienna%') AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Salzburg' WHERE city ILIKE '%Salzburg%' AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Tirol' WHERE city ILIKE '%Innsbruck%' AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Steiermark' WHERE city ILIKE '%Graz%' AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Oberösterreich' WHERE (city ILIKE '%Linz%' OR city ILIKE '%Wels%' OR city ILIKE '%Steyr%') AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Kärnten' WHERE (city ILIKE '%Klagenfurt%' OR city ILIKE '%Villach%') AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Niederösterreich' WHERE (city ILIKE '%Sankt Pölten%' OR city ILIKE '%Wiener Neustadt%') AND (state IS NULL OR state = '');
UPDATE company_addresses SET state = 'Vorarlberg' WHERE (city ILIKE '%Dornbirn%' OR city ILIKE '%Bregenz%' OR city ILIKE '%Feldkirch%') AND (state IS NULL OR state = '');
```

## Troubleshooting

### Error: "column company_addresses.state does not exist"

This error means the migration hasn't been applied yet. Please run the SQL above in your Supabase SQL Editor.

### Error: "column state of relation company_addresses does not exist" during UPDATE

This means the ALTER TABLE command didn't run successfully. Make sure to run the entire SQL block above in one go.

### Where to find your Supabase SQL Editor

1. Log in to https://app.supabase.com
2. Select your project
3. Click on "SQL Editor" in the left sidebar
4. Click "New query"
5. Paste the complete SQL from above
6. Click "Run" (or press Cmd/Ctrl + Enter)
