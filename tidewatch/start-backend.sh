#!/bin/bash
# TideWatch - Start Backend
set -e

cd "$(dirname "$0")/backend"

echo "🌊 Starting TideWatch Backend..."

# Create .env from example if missing
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  Created .env from .env.example (edit with your keys)"
fi

# Install dependencies
pip install -r requirements.txt --quiet

echo "  Starting FastAPI server on http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
