import csv

INPUT_FILE = "../../datasets/raw/icd10cm_order_2026.txt"
OUTPUT_FILE = "../../datasets/icd10_codes.csv"

codes = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    next(f)  # skip header row (Order26 / POAexemptCode / Description)

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

        # The source file wraps some descriptions in literal quote characters
        # (not CSV quoting) when the text itself contains a comma.
        if description.startswith('"') and description.endswith('"'):
            description = description[1:-1]

        codes.append((code, description))

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["code", "description"])
    writer.writerows(codes)

print(f"Saved {len(codes)} ICD-10 codes to icd10_codes.csv")
