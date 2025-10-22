# BizRay

A full-stack application for searching and retrieving company information from the Austrian Business Register (Firmenbuch).

## Project Structure

This monorepo contains two separate applications:

```
bizray/
├── frontend/        # Next.js frontend application
├── backend/         # FastAPI backend service
└── README.md        # This file
```

## Quick Start

### Prerequisites

- **Frontend:** Node.js 18+, pnpm
- **Backend:** Python 3.8+, pip

### Installation

Install all dependencies at once:

```bash
make install
```

Or install them separately:

```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && pnpm install
```

### Running the Application

#### Option 1: Use Make Commands (Easiest)

```bash
make dev          # Run both frontend and backend
make backend      # Run backend only
make frontend     # Run frontend only
make clean        # Clean build artifacts
```

#### Option 2: Use the Development Script

```bash
./dev.sh
```

This will start both the backend and frontend servers automatically.

#### Option 3: Start Services Manually

##### 1. Start the Backend

```bash
cd backend
# Create .env file with API_KEY and WSDL_URL if not exists
python server.py
```

The backend API will run on [http://localhost:8000](http://localhost:8000).

##### 2. Start the Frontend

```bash
cd frontend
pnpm dev
```

The frontend will run on [http://localhost:3000](http://localhost:3000).

## Architecture

### Frontend (`/frontend`)

- **Framework:** Next.js 15.5 with App Router
- **UI:** React 19, Tailwind CSS 4, shadcn/ui
- **Port:** 3000

See [frontend/README.md](./frontend/README.md) for detailed documentation.

### Backend (`/backend`)

- **Framework:** FastAPI 0.111
- **SOAP Client:** Zeep 4.3
- **Port:** 8000

See [backend/README.md](./backend/README.md) for detailed documentation.

## Features

- 🔍 Search companies by name
- 📊 View detailed company information
- 🔒 Secure API proxy to Austrian Business Register
- 🚀 Fast and responsive UI
- 🎨 Modern design with Tailwind CSS

## Development

Both frontend and backend can be developed independently. The frontend makes API calls to the backend at `http://localhost:8000`.

## Environment Variables

### Backend

Create `backend/.env`:

```env
API_KEY=your_api_key_here
WSDL_URL=https://justizonline.gv.at/jop/api/at.gv.justiz.fbw/ws?wsdl
```

## License

Private project for IMC Software Engineering.
