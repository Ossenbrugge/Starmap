#!/bin/bash

echo
echo "========================================="
echo " Starmap - Felgenland Saga v0.0.1"
echo " 3D Interactive Stellar Cartography"
echo "========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo "Please install Python 3.8 or higher"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "ERROR: Python $REQUIRED_VERSION or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        echo "ERROR: pip is not installed"
        echo "Please install pip: $PYTHON_CMD -m ensurepip"
        exit 1
    else
        PIP_CMD="pip"
    fi
else
    PIP_CMD="pip3"
fi

# Install requirements
echo "Checking dependencies..."
$PIP_CMD install -r requirements.txt --quiet

# Start the application
echo
echo "Starting Starmap application..."
echo
echo "========================================"
echo " Access the starmap at:"
echo " http://localhost:8080"
echo
echo " Login credentials:"
echo " Username: admin"
echo " Password: felgenland_secure_2025"
echo "========================================"
echo

$PYTHON_CMD app.py