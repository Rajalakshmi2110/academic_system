#!/bin/bash

echo "🚀 Starting Doubt Clarification System..."

# Start backend
echo "📡 Starting Flask backend on port 5000..."
cd academic_system/api
python app.py &
BACKEND_PID=$!

# Wait for backend
sleep 3

# Start frontend
echo "🎨 Starting React frontend on port 3000..."
cd ../../frontend
npm start &
FRONTEND_PID=$!

echo "✅ System running!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
