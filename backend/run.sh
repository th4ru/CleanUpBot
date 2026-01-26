#!/bin/bash
# Backend startup script for Linux/macOS

echo ""
echo "==================================="
echo "System Manager Backend Startup"
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env file with your settings!"
    echo ""
fi

# Run the application
echo ""
echo "Starting Flask backend..."
echo "Server will run on http://localhost:5000"
echo ""
python app.py
