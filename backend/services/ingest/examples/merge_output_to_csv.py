import os
import pandas as pd
import json

input_dir = "./output"
output_dir = "./merged_output"
os.makedirs(output_dir, exist_ok=True)

companies, links, offices = [], [], []

def try_parse_file(file_path):
    """Try to read a file as JSON, CSV, TSV, or key-value .txt"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()

    # Try JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return pd.DataFrame([data])
        elif isinstance(data, list):
            return pd.DataFrame(data)
    except Exception:
        pass

    # Try CSV / TSV formats
    try:
        if ";" in content:
            return pd.read_csv(file_path, sep=";")
        elif "\t" in content:
            return pd.read_csv(file_path, sep="\t")
        elif "," in content:
            return pd.read_csv(file_path, sep=",")
    except Exception:
        pass

    # Try simple key-value pairs
    lines = [line for line in content.splitlines() if ":" in line]
    if lines:
        pairs = dict(
            [tuple(map(str.strip, line.split(":", 1))) for line in lines if ":" in line]
        )
        return pd.DataFrame([pairs])

    return None


for root, _, files in os.walk(input_dir):
    for file in files:
        file_path = os.path.join(root, file)
        df = try_parse_file(file_path)

        if df is None or df.empty:
            print(f"⚠️ Could not parse: {file}")
            continue

        name = file.lower()
        if "company" in name or "firma" in name:
            companies.append(df)
        elif "link" in name or "connection" in name or "relation" in name:
            links.append(df)
        elif "office" in name or "branch" in name or "standort" in name:
            offices.append(df)
        else:
            # Heuristic: If no keyword, assume it’s company-related
            companies.append(df)

def merge_and_save(dfs, name):
    if not dfs:
        print(f"⚠️ No data found for {name}")
        return
    merged = pd.concat(dfs, ignore_index=True).drop_duplicates()
    merged.to_csv(os.path.join(output_dir, f"{name}.csv"), index=False)
    print(f"✅ Saved {name}.csv with {len(merged)} rows.")

merge_and_save(companies, "companies")
merge_and_save(links, "links")
merge_and_save(offices, "offices")

print("\n🎉 Conversion complete! Files saved in /merged_output")
