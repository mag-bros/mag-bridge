#!/bin/bash
# Electron dev mode (run on macOS host OUTSIDE container)

set -e

cd "$(dirname "$0")"

echo "🖥️  Starting Electron Development Mode"
echo ""
echo "⚠️  Prerequisites:"
echo "   1. Dev container must be running"
echo "   2. Angular dev server must be running on port 4200"
echo "   3. Backend must be running on port 8000"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Electron dependencies (first time)..."
    npm install
fi

echo "⏳ Waiting for Angular dev server at http://localhost:4200..."
npm run dev
