from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
WSDL_URL = os.getenv("WSDL_URL")
FIRMENBUCH_BASE_URL = os.getenv("FIRMENBUCH_BASE_URL")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
NOTIFICATIONS_FROM_EMAIL = os.getenv("NOTIFICATIONS_FROM_EMAIL", "alerts@bizray.local")
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://app.bizray.ai")

