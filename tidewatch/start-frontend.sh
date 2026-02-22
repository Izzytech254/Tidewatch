#!/bin/bash
# TideWatch - Start Frontend
set -e

cd "$(dirname "$0")/frontend"

echo "🌊 Starting TideWatch Frontend..."

# Create .env from example if missing
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  Created .env from .env.example (add your Mapbox token)"
fi

# Install dependencies
npm install --silent

echo "  Starting Vite dev server on http://localhost:5173"
npm run dev
