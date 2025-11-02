# 🚀 Quick Start Guide - BizRay Backend

## Step 1: Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

Then edit `.env` and add your Supabase credentials:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

## Step 2: Setup Database

1. Go to your Supabase Dashboard (https://supabase.com/dashboard)
2. Navigate to **SQL Editor**
3. Copy the contents of `backend/database/migrations/init.sql`
4. Paste and run it in the SQL Editor

This will create all necessary tables:

- ✅ companies
- ✅ officers
- ✅ company_officers
- ✅ links

## Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 4: Run the Server

### Option A: Using the run script

```bash
python3 run.py
```

### Option B: Using uvicorn directly

```bash
uvicorn services.api.main:app --reload --port 8000
```

## Step 5: Test the API

Once running, visit:

- 🏠 Homepage: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- ❤️ Health Check: http://localhost:8000/health

## Quick API Test

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### Search Companies

```bash
curl "http://localhost:8000/api/search/?query=test"
```

### Get All Companies

```bash
curl http://localhost:8000/api/companies/
```

## Available Endpoints

### Companies

- `GET /api/companies/` - List all companies
- `GET /api/companies/{id}` - Get specific company
- `POST /api/companies/` - Create company
- `PUT /api/companies/{id}` - Update company
- `DELETE /api/companies/{id}` - Delete company

### Officers

- `GET /api/officers/` - List all officers
- `GET /api/officers/{id}` - Get specific officer
- `POST /api/officers/` - Create officer

### Search

- `GET /api/search/?query={term}` - Search companies

## Troubleshooting

### Error: "SUPABASE_URL and SUPABASE_KEY must be set"

- Make sure your `.env` file exists and has the correct values
- Restart the server after updating `.env`

### Error: "Connection refused"

- Check if your Supabase database is accessible
- Verify your SUPABASE_URL and SUPABASE_KEY are correct

### Error: "Module not found"

- Run `pip install -r requirements.txt` again
- Make sure you're in the correct directory

## Next Steps

1. Populate database with sample data (optional)
2. Integrate with frontend at http://localhost:3000
3. Configure CORS settings in `services/api/main.py` for production

## Need Help?

Check the full README.md for detailed documentation.
