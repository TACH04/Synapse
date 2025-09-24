#!/bin/bash
# Startup script that ensures virtual environment is activated

echo "🏥 Starting Medical Conversation Simulator..."
echo "📦 Activating virtual environment..."

# Activate virtual environment
source venv/bin/activate

# Check if activation worked
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Virtual environment activated"
else
    echo "❌ Failed to activate virtual environment"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Run the application
python run.py
