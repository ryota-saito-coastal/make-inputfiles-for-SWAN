#!/bin/bash

# Convenience script to create a Python virtual environment
# for running the SWAN preprocessing utilities.
# Execute this file from the repository root.

echo "Creating virtual environment: .venv"
python3 -m venv .venv
source .venv/bin/activate

# Install the Python packages required by the helper scripts
echo "Installing required packages..."
pip install --upgrade pip
pip install \
  xarray \
  numpy \
  matplotlib \
  scipy \
  pandas \
  cartopy

echo "Environment setup complete. Activate with: source .venv/bin/activate"
