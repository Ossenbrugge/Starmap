#!/bin/bash
# Activation script for Starmap virtual environment

echo "🌟 Activating Starmap Virtual Environment"
echo "========================================="

# Check if virtual environment exists
if [ ! -d "starmap_venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv starmap_venv"
    exit 1
fi

# Activate virtual environment
source starmap_venv/bin/activate

# Check if requirements are installed
python -c "import flask, pandas, plotly, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Some requirements missing. Installing..."
    pip install -r requirements.txt
fi

echo "✅ Virtual environment activated successfully!"
echo ""
echo "📋 Available commands:"
echo "  python app.py              - Run Starmap application"
echo "  python test_environment.py - Run environment tests"
echo "  deactivate                 - Exit virtual environment"
echo ""
echo "🚀 You can now run the Starmap application!"