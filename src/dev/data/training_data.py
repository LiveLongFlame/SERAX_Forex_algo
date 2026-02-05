# This script reads a CSV file containing stock data and extracts only the OHLC (Open, High, Low, Close) columns,
# then saves the extracted data to a new CSV file.
import pandas as pd

df = pd.read_csv("combined.csv")

# keep only the columns you care about
ohlc = df[["open", "high", "low", "close"]]

ohlc.to_csv("ohlc.csv", index=False)

