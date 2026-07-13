import csv

INPUT_FILE = "../../datasets/raw/hcpcs_raw.csv"
OUTPUT_FILE = "../../datasets/cpt_codes.csv"

MAX_CODES = 1000

procedures = []

with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        code = row.get("CPT Code")
        desc = row.get("Description")

        if not code or not desc:
            continue

        procedures.append((code.strip(), desc.strip()))

        if len(procedures) >= MAX_CODES:
            break

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["code", "description"])
    writer.writerows(procedures)

print(f"Saved {len(procedures)} CPT-like procedure codes to cpt_codes.csv")
