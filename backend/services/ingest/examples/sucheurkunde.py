from client import create_client
import os
import sys

def search_urkunde_by_fnr(fnr):
    client = create_client()

    output_dir = "output/urkunde"
    os.makedirs(output_dir, exist_ok=True)

    try:
        print(f"🔍 Searching for documents with FNR: {fnr}")
        urkunde_response = client.service.SUCHEURKUNDE(FNR=fnr)

        filename = f"{fnr}_urkunden.txt"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(urkunde_response))

        print(f"✅ Document search result saved to {filepath}")

    except Exception as e:
        print(f"❌ Error during SUCHEURKUNDE for FNR {fnr}: {e}")

if __name__ == "__main__":
    search_urkunde_by_fnr("353435 h")
