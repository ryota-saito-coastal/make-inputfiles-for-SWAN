#!/bin/bash
# setup_env.sh

echo "Creating virtual environment: .venv"
python3 -m venv .venv
source .venv/bin/activate

echo "Installing required packages..."
pip install --upgrade pip

pip install \
  xarray \
  numpy \
  matplotlib \
  scipy \
  pandas \
  cartopy

echo "Environment setup complete."
