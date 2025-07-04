#!/bin/bash
# Script to run Starmap application in virtual environment

echo "🌟 Starting Starmap Application"
echo "==============================="

# Check if virtual environment exists
if [ ! -d "starmap_venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python -m venv starmap_venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source starmap_venv/bin/activate

# Check and install requirements
echo "📦 Checking requirements..."
python -c "import flask, pandas, plotly, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing requirements..."
    pip install -r requirements.txt
    echo "✅ Requirements installed"
else
    echo "✅ All requirements satisfied"
fi

# Ask which version to run
echo ""
echo "🚀 Which option would you like?"
echo "1) Run Starmap Application"
echo "2) Test Environment"
echo "3) Setup Environment"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🏗️  Starting Starmap Application..."
        python app.py
        ;;
    2)
        echo "🧪 Running Environment Test..."
        python test_environment.py
        ;;
    3)
        echo "🔧 Running Environment Setup..."
        python setup_environment.py
        ;;
    *)
        echo "❌ Invalid choice. Starting Starmap application by default..."
        python app.py
        ;;
esac