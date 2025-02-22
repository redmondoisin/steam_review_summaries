#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Check if the virtual environment directory exists; if not, create it.
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting the Flask application..."
python run.py
