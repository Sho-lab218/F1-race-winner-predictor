#!/bin/bash
# Start FastAPI backend server

echo "Starting F1 Prediction API..."
echo "Backend will be available at: http://localhost:8000"
echo "API docs will be at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Activated virtual environment"
fi

# Check if models exist
if [ ! -f "models/model_metadata.pkl" ]; then
    echo "⚠️  Warning: Models not found!"
    echo "   Run 'python3 main.py' first to train models."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the server
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

