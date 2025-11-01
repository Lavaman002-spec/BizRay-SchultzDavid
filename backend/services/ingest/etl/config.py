from dotenv import load_dotenv
import os

# Load environment variables from .env file if it exists
# Look for .env in multiple locations
env_paths = [
    '.env',  # Current directory
    os.path.join(os.path.dirname(__file__), '.env'),  # Same dir as this file
    os.path.join(os.path.dirname(__file__), '../../../.env'),  # Project root
    os.path.join(os.path.dirname(__file__), '../../../../.env'),  # Root above backend
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✓ Loaded .env from: {env_path}")
        break
else:
    # Also try loading from default location
    load_dotenv()

# API Configuration
API_KEY = os.getenv("API_KEY")
WSDL_URL = os.getenv("WSDL_URL", "https://justizonline.gv.at/jop/api/at.gv.justiz.fbw/ws?wsdl")

# Validate required configuration
if not API_KEY:
    print("⚠️ Warning: API_KEY not set in environment variables")
    print("   Set API_KEY in .env file or environment")

# Database Configuration (with both Docker and local defaults)
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "bizray")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")