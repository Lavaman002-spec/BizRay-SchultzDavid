import os
from dotenv import load_dotenv

print("Current working directory:", os.getcwd())
print("\nLooking for .env file...")

# Try to load .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
WSDL_URL = os.getenv("WSDL_URL")

print(f"\nAPI_KEY loaded: {bool(API_KEY)}")
print(f"API_KEY value: {API_KEY}")
print(f"\nWSDL_URL loaded: {bool(WSDL_URL)}")
print(f"WSDL_URL value: {WSDL_URL}")

if not API_KEY or not WSDL_URL:
    print("\n❌ ERROR: Environment variables not loaded correctly!")
else:
    print("\n✅ Environment variables loaded successfully!")