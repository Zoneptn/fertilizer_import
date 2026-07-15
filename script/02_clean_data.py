# ==========================================
# 02_clean_data.py
# Clean extracted fertilizer import data
# ==========================================

from pathlib import Path
import pandas as pd
import re

# ==========================================
# Project folders
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FOLDER = PROJECT_ROOT / "data" / "extracted_excel"
OUTPUT_FOLDER = PROJECT_ROOT / "data" / "cleaned"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ==========================================
# Cleaning Functions
# ==========================================

def clean_formula(df):
    """
    Replace Thai fertilizer names with
    'Secondary & Micronutrient'
    """

    mask = ~df["Formula"].astype(str).str.match(r"^\d+(-\d+)+$", na=False)

    df.loc[mask, "Formula"] = "Secondary & Micronutrient"

    return df


def convert_numeric(df):
    """
    Convert import volume and value to numeric.
    """

    numeric_columns = [
        "Import_Volume_TON",
        "Import_Value_THB"
    ]

    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip(),
            errors="coerce"
        )

    return df


def add_year(df, filename):
    """
    Extract year from filename.

    Example:
    fertilizer_import_2026_raw.xlsx
                    ↓
                  2026
    """

    match = re.search(r"(20\d{2})", filename)

    if match:
        df["Year"] = int(match.group(1))
    else:
        df["Year"] = None

    return df


def calculate_average_price(df):
    """
    Calculate average import price (Baht per TON).
    """

    df["AVG_price_THB_per_TON"] = (
        df["Import_Value_THB"] /
        df["Import_Volume_TON"]
    )

    return df


# ==========================================
# Clean one file
# ==========================================

def clean_file(file_path):

    df = pd.read_excel(file_path)

    df = clean_formula(df)

    df = convert_numeric(df)

    df = add_year(df, file_path.name)

    df = calculate_average_price(df)

    return df


# ==========================================
# Main
# ==========================================

def main():

    excel_files = sorted(INPUT_FOLDER.glob("*.xlsx"))

    if not excel_files:
        print("No extracted Excel files found.")
        return

    for file in excel_files:

        print(f"Cleaning {file.name}...")

        df = clean_file(file)

        output_name = file.stem.replace("_raw", "_clean") + ".xlsx"

        output_path = OUTPUT_FOLDER / output_name

        df.to_excel(output_path, index=False)

        print(f"Saved -> {output_name}")

    print("\nCleaning complete!")


if __name__ == "__main__":
    main()