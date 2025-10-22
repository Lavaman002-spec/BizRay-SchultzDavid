# BizRay Backend

FastAPI backend service that provides a proxy to the Austrian Business Register (Firmenbuch) SOAP API.

## Getting Started

### Prerequisites

- Python 3.8+
- pip or pipenv

### Installation

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
API_KEY=your_api_key_here
WSDL_URL=https://justizonline.gv.at/jop/api/at.gv.justiz.fbw/ws?wsdl
```

### Development

Run the development server:

```bash
python server.py
```

The API will be available at [http://localhost:8000](http://localhost:8000).

## API Endpoints

### Health Check

- `GET /healthz` - Health check endpoint

### Debug Endpoints

- `GET /debug` - Enhanced debug information
- `GET /test-wsdl` - Test WSDL accessibility
- `GET /inspect-endpoints` - Inspect SOAP service endpoints
- `GET /test-soap-endpoint` - Test SOAP endpoint response

### Business Registry

- `GET /search?q={query}` - Search for companies by name

  - **Parameters:**
    - `q` (required): Search query, minimum 2 characters
  - **Returns:** List of companies with FNR and name

- `GET /company/{fnr}` - Get detailed company information
  - **Parameters:**
    - `fnr` (required): Company registration number (Firmenbuchnummer)
  - **Returns:** Detailed company information

## Project Structure

```
backend/
├── proxy.py          # Main FastAPI application
├── server.py         # Uvicorn server entry point
├── requirements.txt  # Python dependencies
├── test_env.py       # Environment testing utility
└── .env             # Environment variables (not in git)
```

## Tech Stack

- **Framework:** FastAPI 0.111
- **ASGI Server:** Uvicorn 0.30
- **SOAP Client:** Zeep 4.3
- **Environment:** python-dotenv 1.0

## CORS Configuration

The backend is configured to accept requests from:

- `http://localhost:3000` (frontend development server)

To modify allowed origins, edit the `allow_origins` parameter in `proxy.py`.

## Development Notes

- The service caches the SOAP client after first initialization
- WSDL endpoints are automatically rewritten from internal (`intra.gv.at`) to public (`justizonline.gv.at`) domains
- All requests require a valid API key set in the `.env` file
