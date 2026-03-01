#!/usr/bin/env bash
# exit on error
set -o errexit

# Force Python 3.11 if available
if command -v python3.11 &> /dev/null; then
    export PYTHON_BIN=python3.11
else
    export PYTHON_BIN=python3
fi

echo "Using Python: $($PYTHON_BIN --version)"

echo "Installing Python dependencies..."
$PYTHON_BIN -m pip install --upgrade pip
$PYTHON_BIN -m pip install --prefer-binary -r requirements.txt

echo "Installing Playwright browsers..."
$PYTHON_BIN -m playwright install chromium
$PYTHON_BIN -m playwright install-deps chromium

echo "Build complete!"
