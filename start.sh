#!/usr/bin/env bash
echo "========================================================"
echo "  GRIDWISE AI - Starting Backend and Frontend Services"
echo "========================================================"

# Start backend
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend running with PID: $BACKEND_PID"

# Start frontend
npm run dev --prefix frontend &
FRONTEND_PID=$!
echo "Frontend running with PID: $FRONTEND_PID"

echo "========================================================"
echo "  GRIDWISE AI is online!"
echo "  Dashboard UI: http://localhost:3000"
echo "  API Docs:     http://127.0.0.1:8000/docs"
echo "========================================================"

wait $BACKEND_PID $FRONTEND_PID
