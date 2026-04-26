#!/bin/bash
# Dev mode: Start Angular dev server (runs in container)
# For Electron, run 'cd electron && npm run dev' on macOS host

set -e

echo "🚀 Starting MagBridge Development Mode (Angular only)"
echo ""
echo "ℹ️  This starts Angular dev server in the container"
echo "ℹ️  For Electron: Run 'cd electron && npm run dev' on macOS host"
echo ""

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🔥 Starting Angular with HMR on http://0.0.0.0:4200"
npm run serve-reloader
