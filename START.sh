#!/bin/bash
# File Converter - Quick Start Script for macOS/Linux

echo ""
echo "====================================="
echo "  FILE CONVERTER PRO - Quick Start"
echo "====================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found! Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Please install Node.js 16+"
    exit 1
fi

echo "✅ Python version:"
python3 --version

echo ""
echo "✅ Node.js version:"
node --version

echo ""
echo "====================================="
echo "  Starting Backend (Flask)"
echo "====================================="
echo ""

cd backend-python

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Backend starting on http://localhost:5000"
echo "Press CTRL+C to stop the backend"
echo ""

python app.py &
BACKEND_PID=$!

echo ""
echo "Waiting 3 seconds for backend to start..."
sleep 3

echo ""
echo "====================================="
echo "  Starting Frontend (React)"
echo "====================================="
echo ""

cd ../converter/frontend

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo ""
echo "✅ Frontend starting on http://localhost:3000"
echo "Press CTRL+C to stop the frontend"
echo ""
echo "Opening browser..."

# Try to open in default browser
if command -v open &> /dev/null; then
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
fi

npm start

# Kill backend when frontend stops
kill $BACKEND_PID 2>/dev/null
