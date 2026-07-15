# ==========================================
# 03_merge_master.py
# Merge cleaned fertilizer import data
# into the master dataset
# ==========================================

from pathlib import Path
import pandas as pd

# ==========================================
# Project folders
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FOLDER = PROJECT_ROOT / "data" / "cleaned"
MASTER_FOLDER = PROJECT_ROOT / "data" / "merged"

MASTER_FOLDER.mkdir(parents=True, exist_ok=True)

MASTER_FILE = MASTER_FOLDER / "fertilizer_import_master.xlsx"


# ==========================================
# Read master file
# ==========================================

if MASTER_FILE.exists():
    master = pd.read_excel(MASTER_FILE)
    print(f"Loaded master file ({len(master):,} rows)")
else:
    master = pd.DataFrame()
    print("Master file not found.")
    print("Creating a new master file...")


# ==========================================
# Read all cleaned files
# ==========================================

excel_files = sorted(INPUT_FOLDER.glob("*_clean.xlsx"))

if not excel_files:
    print("No cleaned files found.")
    exit()


# ==========================================
# Merge all cleaned files
# ==========================================

for file in excel_files:

    print(f"Merging {file.name}...")

    df = pd.read_excel(file)

    master = pd.concat(
        [master, df],
        ignore_index=True
    )


# ==========================================
# Remove duplicates
# ==========================================

before = len(master)

master = master.drop_duplicates()

after = len(master)

print(f"Removed {before-after:,} duplicate rows.")


# ==========================================
# Sort data
# ==========================================

master = (
    master
    .sort_values(
        by=["Year", "Formula"]
    )
    .reset_index(drop=True)
)


# ==========================================
# Save
# ==========================================

master.to_excel(
    MASTER_FILE,
    index=False
)

print(f"\nMaster file updated successfully.")
print(f"Total rows: {len(master):,}")
print(f"Saved to:\n{MASTER_FILE}")