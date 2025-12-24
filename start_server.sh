#!/bin/bash
# Simple script to start the restaurant app server

echo "======================================================================"
echo "🍽️  Restaurant Reviews Map - Starting Server..."
echo "======================================================================"
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    python3 run_restaurant_app.py
elif command -v python &> /dev/null; then
    python run_restaurant_app.py
else
    echo "❌ Error: Python is not installed!"
    echo "   Please install Python 3 to run this application"
    exit 1
fi
