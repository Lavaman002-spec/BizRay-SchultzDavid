#!/bin/bash
# Bulk Ingestion Quick Start Script
# This script helps you quickly run bulk API ingestion

set -e  # Exit on error

echo "========================================================================"
echo "🚀 BizRay Bulk API Ingestion - Quick Start"
echo "========================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../../.."

echo "📂 Project root: $PROJECT_ROOT"
echo ""

# Check if .env exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}❌ Error: .env file not found at $PROJECT_ROOT/.env${NC}"
    echo "   Please create .env file with required configuration"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found .env file"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    echo "   Please start Docker Desktop"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is running"

# Check if database container is running
if ! docker ps | grep -q postgres; then
    echo -e "${YELLOW}⚠️  Database container not running. Starting it now...${NC}"
    cd "$PROJECT_ROOT"
    docker-compose up -d db
    echo "   Waiting for database to be ready (10 seconds)..."
    sleep 10
fi

echo -e "${GREEN}✓${NC} Database container is running"

# Parse command line arguments
MAX_COMPANIES=100
DELAY=1.0
NO_DISCOVERY=false
SPECIFIC_COMPANIES=""
SKIP_NORMALIZE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --max)
            MAX_COMPANIES="$2"
            shift 2
            ;;
        --delay)
            DELAY="$2"
            shift 2
            ;;
        --no-discovery)
            NO_DISCOVERY=true
            shift
            ;;
        --companies)
            shift
            SPECIFIC_COMPANIES="$@"
            break
            ;;
        --skip-normalize)
            SKIP_NORMALIZE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --max N              Maximum number of companies to fetch (default: 100)"
            echo "  --delay SECONDS      Delay between API requests (default: 1.0)"
            echo "  --no-discovery       Skip discovery, use sample companies"
            echo "  --companies FN1 FN2  Fetch specific companies by register ID"
            echo "  --skip-normalize     Skip normalization step"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --max 100"
            echo "  $0 --companies FN348406 FN10001 FN10002"
            echo "  $0 --max 50 --delay 0.5"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo ""
echo "========================================================================"
echo "📋 Configuration"
echo "========================================================================"
echo "Max Companies:    $MAX_COMPANIES"
echo "Request Delay:    ${DELAY}s"
echo "Use Discovery:    $([ "$NO_DISCOVERY" = true ] && echo "No" || echo "Yes")"
echo "Skip Normalize:   $([ "$SKIP_NORMALIZE" = true ] && echo "Yes" || echo "No")"
if [ -n "$SPECIFIC_COMPANIES" ]; then
    echo "Specific IDs:     $SPECIFIC_COMPANIES"
fi
echo ""

# Ask for confirmation
read -p "Proceed with ingestion? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled by user"
    exit 0
fi

echo ""
echo "========================================================================"
echo "🔄 Starting Bulk Ingestion..."
echo "========================================================================"
echo ""

# Build Python command
cd "$SCRIPT_DIR"
PYTHON_CMD="python run_bulk_ingest.py --max $MAX_COMPANIES --delay $DELAY"

if [ "$NO_DISCOVERY" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --no-discovery"
fi

if [ "$SKIP_NORMALIZE" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --skip-normalize"
fi

if [ -n "$SPECIFIC_COMPANIES" ]; then
    PYTHON_CMD="$PYTHON_CMD --companies $SPECIFIC_COMPANIES"
fi

# Run the ingestion
echo "Running: $PYTHON_CMD"
echo ""

eval $PYTHON_CMD

EXIT_CODE=$?

echo ""
echo "========================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Bulk Ingestion Completed Successfully!${NC}"
    echo "========================================================================"
    echo ""
    echo "📊 Next Steps:"
    echo ""
    echo "1. Check the data in your database:"
    echo "   docker exec -it bizray-db-1 psql -U postgres -d bizray -c 'SELECT COUNT(*) FROM companies;'"
    echo ""
    echo "2. Start the API service:"
    echo "   cd $PROJECT_ROOT && docker-compose up -d api_service"
    echo ""
    echo "3. Query the API:"
    echo "   curl 'http://localhost:8080/api/companies/search?q=company'"
    echo ""
    echo "4. Start the frontend:"
    echo "   cd $PROJECT_ROOT/frontend && npm run dev"
    echo ""
else
    echo -e "${RED}❌ Bulk Ingestion Failed${NC}"
    echo "========================================================================"
    echo ""
    echo "Check the error messages above for details."
    echo "Common issues:"
    echo "  - Database connection problems"
    echo "  - API authentication issues"
    echo "  - Missing dependencies"
    echo ""
    echo "For help, see: BULK_INGESTION_GUIDE.md"
fi

exit $EXIT_CODE
