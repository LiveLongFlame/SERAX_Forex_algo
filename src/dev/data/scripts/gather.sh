#!/bin/bash

set -e 

echo "Running extracting_data.py..."
python3 ../code/extracting_data.py

echo "Running combine_csv_files.py..."
python3 ../code/combine_csv_files.py

echo "Running training_data.py..."
python3 ../codetraining_data.py

echo "All scripts executed successfully."
