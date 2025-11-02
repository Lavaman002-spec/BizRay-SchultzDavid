from client import create_client
import os

def test_suchefirma():
    client = create_client()

    # Prepare input parameters
    params = {
        "FIRMENWORTLAUT": "*",
        "EXAKTESUCHE": False,
        "SUCHBEREICH": 1,  # Adjust based on API docs
        "GERICHT": "",     # Optional or specific court name
        "RECHTSFORM": "GES",  # Optional or specific legal form
        "RECHTSEIGENSCHAFT": "",  # Optional or specific legal attribute
        "ORTNR": "90001"        # Optional or specific location number
    }

    # Call the method
    response = client.service.SUCHEFIRMA(**params)

    # Print the response
    print(f"Response has {len(response.ERGEBNIS)} results.")


    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "suchergebnis.txt")
    # Save response to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(response))

if __name__ == "__main__":
    test_suchefirma()
