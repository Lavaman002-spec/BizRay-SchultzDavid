from client import create_client
from datetime import date
import os
import sys

def get_urkunde(key):
    client = create_client()

    output_dir = "output/urkunde"
    os.makedirs(output_dir, exist_ok=True)

    stichtag = date.today().isoformat()

    try:
        print(f"🔍 Requesting URKUNDE for KEY: {key} on {stichtag}")
        response = client.service.URKUNDE(KEY=key)

        filename = f"{key}_urkunde.txt"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(response))

        print(f"✅ URKUNDE saved to {filepath}")

    except Exception as e:
        print(f"❌ Error calling URKUNDE for KEY {key}: {e}")

if __name__ == "__main__":
    get_urkunde("056247_5690452507182_000___000_30_36803752_XML")
