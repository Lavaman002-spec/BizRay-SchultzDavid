# BizRay Backend

FastAPI backend for Austrian Business Register (Firmenbuch) data management.

## Features

- FastAPI framework with automatic API documentation
- Supabase database integration
- Company search functionality
- Officer management
- Company relationships tracking
- RESTful API endpoints

## Setup

### Prerequisites

- Python 3.9+
- Supabase account and database
- pip or poetry for package management

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

3. Update `.env` with your Supabase credentials:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

4. Run database migrations in Supabase:
   - Go to your Supabase dashboard
   - Navigate to SQL Editor
   - Copy and run the contents of `supabase/migrations/init.sql`

### Running the Application

#### Development Mode

```bash
cd backend
uvicorn services.api.main:app --reload --port 8000
```

The API will be available at:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Production Mode

```bash
uvicorn services.api.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Companies

- `GET /api/companies/` - List all companies
- `GET /api/companies/{id}` - Get company by ID (includes officers)
- `GET /api/companies/fn/{fn_number}` - Get company by Firmenbuch number
- `POST /api/companies/` - Create new company
- `PUT /api/companies/{id}` - Update company
- `DELETE /api/companies/{id}` - Delete company

### Officers

- `GET /api/officers/` - List all officers
- `GET /api/officers/{id}` - Get officer by ID
- `GET /api/officers/company/{company_id}` - Get officers by company
- `POST /api/officers/` - Create new officer
- `PUT /api/officers/{id}` - Update officer
- `DELETE /api/officers/{id}` - Delete officer

### Search

- `GET /api/search/?query={term}` - Search companies
- `POST /api/search/` - Search with advanced options

### Health

- `GET /health` - Health check endpoint
- `GET /` - API information

## Database Schema

### Tables

- **companies**: Company information (FN number, name, address, etc.)
- **officers**: Officer/director information
- **company_officers**: Junction table linking companies and officers
- **links**: Company relationships/connections

## Project Structure

```
backend/
├── services/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   ├── dependencies.py      # Dependency injection
│   │   └── routers/
│   │       ├── companies.py     # Company endpoints
│   │       ├── officers.py      # Officer endpoints
│   │       └── search.py        # Search endpoints
│   └── ingest/                  # Data ingestion services
├── shared/
│   ├── config.py                # Configuration
│   ├── models.py                # Pydantic models
│   └── utils.py                 # Utility functions
├── supabase/
│   ├── client.py                # Supabase client
│   ├── queries.py               # Database queries
│   └── migrations/
│       └── init.sql             # Database schema
└── requirements.txt             # Python dependencies
```

## Environment Variables

| Variable       | Description                        | Required |
| -------------- | ---------------------------------- | -------- |
| `SUPABASE_URL` | Supabase project URL               | Yes      |
| `SUPABASE_KEY` | Supabase anon/public key           | Yes      |
| `API_KEY`      | Austrian Business Register API key | No       |
| `WSDL_URL`     | WSDL endpoint URL                  | No       |

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black backend/
```

### Linting

```bash
flake8 backend/
```

## API Documentation

Once the server is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License
