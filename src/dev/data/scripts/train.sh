#!/bin/bash

set -e 


echo "Running combine_csv_files.py..."
python3 combine_csv_files.py

echo "Running training_data.py..."
python3 training_data.py

echo "All scripts executed successfully."
