# ==========================================
# 01_extract_pdf.py
# Extract fertilizer import PDF to Excel
# ==========================================

from pathlib import Path
import pandas as pd
import pdfplumber

# ==========================================
# Project folders
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_PDF_FOLDER = PROJECT_ROOT / "data" / "raw_pdf"
OUTPUT_FOLDER = PROJECT_ROOT / "data" / "extracted_excel"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# ==========================================
# Extract one PDF
# ==========================================

def extract_pdf(pdf_path):

    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                df = pd.DataFrame(table)

                if df.empty:
                    continue

                # Remove repeated header
                if str(df.iloc[0, 0]).strip() == "ลําดับ":
                    df = df.iloc[1:].reset_index(drop=True)

                # Remove No. column
                df = df.drop(columns=[0])

                # Rename columns
                df.columns = [
                    "Formula",
                    "Import_Volume_TON",
                    "Import_Value_THB"
                ]

                all_tables.append(df)

    if len(all_tables) == 0:
        print(f"No tables found in {pdf_path.name}")
        return None

    master = pd.concat(all_tables, ignore_index=True)

    return master


# ==========================================
# Main
# ==========================================

def main():

    pdf_files = sorted(RAW_PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found.")
        return

    for pdf in pdf_files:

        print(f"Extracting {pdf.name}...")

        master = extract_pdf(pdf)

        if master is None:
            continue

        output_file = OUTPUT_FOLDER / f"{pdf.stem}_raw.xlsx"

        master.to_excel(output_file, index=False)

        print(f"Saved -> {output_file.name}")

    print("\nFinished!")


if __name__ == "__main__":
    main()