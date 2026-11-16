#!/usr/bin/env bash
set -e

# Multiverse Launcher
echo "=================================================="
echo "    MULTIVERSE — One question. Multiple minds.    "
echo "=================================================="

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start Backend
echo "Starting Backend on http://127.0.0.1:8000..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend on http://localhost:5173..."
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

trap "echo 'Shutting down Multiverse...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" SIGINT SIGTERM EXIT

wait
