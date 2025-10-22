#!/bin/bash
# Development script to run both frontend and backend

echo "Starting BizRay Development Environment"
echo ""

# Check if backend/.env exists
if [ ! -f "backend/.env" ]; then
    echo "Warning: backend/.env not found!"
    echo "Please create backend/.env with API_KEY and WSDL_URL"
    exit 1
fi

# Start backend in background
echo "📦 Starting Backend (FastAPI) on http://localhost:8000"
cd backend
python server.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting Frontend (Next.js) on http://localhost:3000"
cd frontend
pnpm dev

# When frontend stops, kill backend too
echo "Stopping services..."
kill $BACKEND_PID
