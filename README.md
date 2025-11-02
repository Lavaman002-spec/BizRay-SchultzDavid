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
cd backend && pip install -r requirment.txt
cd frontend && npm i
```

### Running the Application

#### Option 1: Use Make Commands (Easiest)

backend

```bash
cd backend && python run.py
```

frontend

```bash
cd frontned && npm run dev
```

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

## Development

Both frontend and backend can be developed independently. The frontend makes API calls to the backend at `http://localhost:8000`.

## Environment Variables

### Backend

Create `backend/.env`:

```env
API_KEY=your_api_key_here
WSDL_URL=https://justizonline.gv.at/jop/api/at.gv.justiz.fbw/ws?wsdl
```
