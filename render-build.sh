#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Updating pip and installing requirements..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "Installing Playwright browsers..."
# This is crucial for our Reddit/LinkedIn scrapers
python -m playwright install chromium
