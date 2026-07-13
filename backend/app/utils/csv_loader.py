import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

def load_icd_codes():
    file_path = BASE_DIR / "datasets" / "icd10_codes.csv"
    return pd.read_csv(file_path)

def load_cpt_codes():
    file_path = BASE_DIR / "datasets" / "cpt_codes.csv"
    return pd.read_csv(file_path)
