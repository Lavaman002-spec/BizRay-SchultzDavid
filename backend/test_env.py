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


from entity_utils import normalize_entity, deduplicate_entities

if __name__ == "__main__":
    data = [
        {"id": 1, "name": "  John Doe ", "email": "JOHN@EXAMPLE.COM"},
        {"id": 2, "name": "john doe", "email": "john@example.com"},
        {"id": 3, "name": "Jane Doe", "email": "jane@example.com"},
    ]

    for d in data:
        normalize_entity(d, ["name", "email"])

    clean_data = deduplicate_entities(data, "email")

    print("After normalization:")
    for d in data:
        print(d)

    print("\nAfter deduplication:")
    for d in clean_data:
        print(d)