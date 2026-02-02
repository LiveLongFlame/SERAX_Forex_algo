#!/bin/bash
# setup.sh - Install dependencies for SERAX_Forex_algo (Python only)

set -e

echo "Updating package lists..."
sudo apt update

echo "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git wget

echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python dependencies..."
pip install pandas ib_insync numpy matplotlib

echo "Installation complete!"
echo "To activate the Python environment, run: source venv/bin/activate"

