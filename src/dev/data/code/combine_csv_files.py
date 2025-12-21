# This program reads all CSV files in ./data and combines them
import pandas as pd
import glob
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(BASE_DIR, "combined.csv")

# Helper to sort by chunk number
def extract_chunk_num(filename):
    match = re.search(r"chunk(\d+)", filename)
    return int(match.group(1)) if match else -1

csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
csv_files = sorted(csv_files, key=extract_chunk_num)

if not csv_files:
    print(f"No CSV files found in {DATA_DIR}")
    sys.exit(1)

df_list = []
expected_columns = None

for f in csv_files:
    try:
        df = pd.read_csv(f)

        if df.empty:
            print(f"Skipping empty file: {os.path.basename(f)}")
            continue

        if expected_columns is None:
            expected_columns = df.columns
        elif not df.columns.equals(expected_columns):
            print(f"Column mismatch in {os.path.basename(f)} — skipping")
            continue

        df_list.append(df)
        print(f"Loaded {os.path.basename(f)} ({len(df)} rows)")

    except Exception as e:
        print(f"Failed to read {os.path.basename(f)}: {e}")

if not df_list:
    print("No valid CSV files to combine.")
    sys.exit(1)

combined_df = pd.concat(df_list, ignore_index=True)
combined_df.to_csv(OUTPUT_FILE, index=False)

print(f"\nCombined {len(df_list)} files into {OUTPUT_FILE}")
print(f"Total rows: {len(combined_df)}")

