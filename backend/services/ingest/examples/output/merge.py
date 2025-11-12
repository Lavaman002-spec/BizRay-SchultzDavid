import ast
import json
import csv

# Step 1: Read the source text file
with open("suchergebnis.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Step 2: Safely evaluate Python-style dict into a Python object
# (the file uses single quotes, not valid JSON)
data = ast.literal_eval(content)

# Step 3: Write proper JSON
with open("suchergebnis.json", "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

# Step 4: Flatten the JSON and export to CSV
rows = []
for entry in data["ERGEBNIS"]:
    rows.append({
        "FNR": entry.get("FNR"),
        "STATUS": entry.get("STATUS"),
        "NAME": " ".join(entry.get("NAME", [])),
        "SITZ": entry.get("SITZ"),
        "RECHTSFORM_CODE": entry.get("RECHTSFORM", {}).get("CODE"),
        "RECHTSFORM_TEXT": entry.get("RECHTSFORM", {}).get("TEXT"),
        "GERICHT_CODE": entry.get("GERICHT", {}).get("CODE"),
        "GERICHT_TEXT": entry.get("GERICHT", {}).get("TEXT"),
    })

# Step 5: Write to CSV
csv_filename = "suchergebnis.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Conversion complete!\n- JSON saved as 'suchergebnis.json'\n- CSV saved as 'suchergebnis.csv'")
