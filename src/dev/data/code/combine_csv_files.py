# This program reads all CSV files in ./data and combines them

import pandas as pd
import glob
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(BASE_DIR, "combined.csv")

csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

if not csv_files:
    print(f"No CSV files found in {DATA_DIR}")
    sys.exit(1)

df_list = [pd.read_csv(f) for f in csv_files]
combined_df = pd.concat(df_list, ignore_index=True)

combined_df.to_csv(OUTPUT_FILE, index=False)

print(f"Combined {len(csv_files)} files into {OUTPUT_FILE}")

