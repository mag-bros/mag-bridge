#!/bin/bash
# Full stack development mode: Angular + Backend (runs in container)

set -e

echo "🚀 Starting MagBridge Full Stack Development Mode"
echo ""
echo "📦 Services:"
echo "   - Angular dev server (port 4200)"
echo "   - FastAPI backend (port 8000)"
echo ""

cd "$(dirname "$0")"

# Check if node_modules exists for Angular
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing Angular dependencies..."
    cd frontend && npm install && cd ..
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: uv venv .venv && uv pip install -r requirements.txt"
    exit 1
fi

# Kill existing processes on ports (if any)
echo "🧹 Cleaning up existing processes..."
lsof -ti:4200 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start Backend in background
echo "🔧 Starting Backend on http://0.0.0.0:8000..."
NODE_ENV=development .venv/bin/python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start Angular
echo "🎨 Starting Angular on http://0.0.0.0:4200..."
cd frontend
npm run serve-reloader &
ANGULAR_PID=$!

cd ..

echo ""
echo "✅ Services started!"
echo "   📡 Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
echo "   📡 API Docs: http://localhost:8000/docs"
echo "   🌐 Angular:  http://localhost:4200 (PID: $ANGULAR_PID)"
echo ""
echo "🔍 Logs:"
echo "   Backend: See terminal output above"
echo "   Angular: See terminal output above"
echo ""
echo "⚠️  Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C and cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $ANGULAR_PID 2>/dev/null || true
    lsof -ti:4200 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

trap cleanup INT TERM

# Wait for processes
wait
