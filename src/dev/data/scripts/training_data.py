# This script reads a CSV file containing stock data and extracts only the OHLC (Open, High, Low, Close) columns,
# then saves the extracted data to a new CSV file.
import pandas as pd
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
COMBINED_FILE = os.path.join(DATA_DIR, "combined.csv")
OHLC_CSV = os.path.join(DATA_DIR, "ohlc.csv")

df = pd.read_csv(COMBINED_FILE)

# keep only the columns you care about
ohlc = df[["open", "high", "low", "close"]]

ohlc.to_csv(OHLC_CSV, index=False)

