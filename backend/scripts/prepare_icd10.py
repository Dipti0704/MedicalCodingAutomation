import csv

INPUT_FILE = "../../datasets/raw/icd10cm_order_2026.txt"
OUTPUT_FILE = "../../datasets/icd10_codes.csv"

MAX_CODES = 3000

codes = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        parts = line.split(maxsplit=2)

        # Expected format:
        # OrderNumber  ICDCode  Description
        if len(parts) < 3:
            continue

        _, code, description = parts

        # Basic validation
        if not code[0].isalnum():
            continue

        codes.append((code, description))

        if len(codes) >= MAX_CODES:
            break

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["code", "description"])
    writer.writerows(codes)

print(f"✅ Saved {len(codes)} ICD-10 codes to icd10_codes.csv")
