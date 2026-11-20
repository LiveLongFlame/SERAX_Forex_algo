
"""
Combines all IBKR historical Forex CSV chunks into:
    - combined.csv: Complete historical dataset
    - ohlc.csv: Date, currency pair and OHLC data
"""

import pandas as pd
import glob
import os
import re
import sys

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATION_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_DIR = os.path.join(LOCATION_DIR, "gathered_data")

COMBINED_FILE = os.path.join(LOCATION_DIR, "combined.csv")
OHLC_FILE = os.path.join(LOCATION_DIR, "ohlc.csv")

# Required columns
REQUIRED_COLUMNS = ["date", "open", "high", "low", "close"]


def extract_sort_key(filename):
    """
    Sort by currency pair and then chunk number.
    Example: EUR_USD_chunk10.csv
    """
    name = os.path.basename(filename)

    match = re.search(r"(.+)_chunk(\d+)\.csv$", name)

    if match:
        pair = match.group(1)
        chunk = int(match.group(2))
        return pair, chunk

    return name, -1


# Find CSV files
csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

# Sort files
csv_files = sorted(csv_files, key=extract_sort_key)

if not csv_files:
    print(f"No CSV files found in {DATA_DIR}")
    sys.exit(1)

print(f"Found {len(csv_files)} CSV files\n")

df_list = []

# Read each CSV
for file in csv_files:
    filename = os.path.basename(file)

    try:
        df = pd.read_csv(file)

        if df.empty:
            print(f"Skipping empty file: {filename}")
            continue

        # Check required columns
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

        if missing:
            print(f"Skipping {filename}: Missing columns {missing}")
            continue

        # Extract currency pair from filename
        match = re.match(r"(.+)_chunk\d+\.csv$", filename)

        if match:
            df["pair"] = match.group(1)
        else:
            print(f"Warning: Could not identify currency pair in {filename}")
            continue

        df_list.append(df)

        print(f"Loaded {filename}: {len(df)} rows")

    except Exception as e:
        print(f"Failed to read {filename}: {e}")


if not df_list:
    print("\nNo valid CSV files to combine.")
    sys.exit(1)


# Combine all datasets
combined_df = pd.concat(df_list, ignore_index=True)

# Convert date column into datetime
# Convert all timestamps to UTC
combined_df["date"] = pd.to_datetime(
    combined_df["date"],
    errors="coerce",
    utc=True
)

# Remove invalid timestamps
combined_df = combined_df.dropna(subset=["date"])

# Sort chronologically, keeping currency pairs separate
combined_df = combined_df.sort_values(
    by=["pair", "date"]
).reset_index(drop=True)

# Remove duplicate candles for the same pair and timestamp
before = len(combined_df)

combined_df = combined_df.drop_duplicates(
    subset=["pair", "date"],
    keep="last"
).reset_index(drop=True)

duplicates = before - len(combined_df)

# Save complete dataset
combined_df.to_csv(COMBINED_FILE, index=False)


# Generate OHLC dataset
ohlc_df = combined_df[
    ["date", "pair", "open", "high", "low", "close"]
].copy()

ohlc_df.to_csv(OHLC_FILE, index=False)


# Summary
print("\n" + "=" * 45)
print("DATA EXTRACTION SUMMARY")
print("=" * 45)

print(f"Files processed: {len(df_list)}")
print(f"Total candles:   {len(combined_df):,}")
print(f"Duplicates:      {duplicates:,}")

print("\nCandles per currency pair:")

print(
    combined_df.groupby("pair").size().to_string()
)

print("\nOutput files:")
print(f"Combined: {COMBINED_FILE}")
print(f"OHLC:     {OHLC_FILE}")

print("\nCompleted successfully!")

