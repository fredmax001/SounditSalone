#!/bin/bash
# Mobile Development Helper
# Run this to expose both frontend and backend to your local network
# Access from your phone at: http://<your-ip>:5173

set -e

# Detect local IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}')

if [ -z "$LOCAL_IP" ]; then
    echo "❌ Could not detect your local IP address."
    echo "   Make sure your computer and phone are on the same WiFi network."
    exit 1
fi

echo "📱 Mobile Dev Mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   Your IP:     http://${LOCAL_IP}:5173"
echo "   Backend:     http://${LOCAL_IP}:8000"
echo ""
echo "   On your phone, open:"
echo "   👉 http://${LOCAL_IP}:5173"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Export for backend CORS
export CORS_ORIGINS="http://localhost:5173,http://${LOCAL_IP}:5173"

# Start backend in background
echo "🚀 Starting backend on 0.0.0.0:8000 ..."
cd "$(dirname "$0")/.."
python main.py &
BACKEND_PID=$!

# Wait for backend
sleep 2

# Start frontend with network API URL
echo "🚀 Starting frontend on 0.0.0.0:5173 ..."
cd app
VITE_API_URL="http://${LOCAL_IP}:8000/api/v1" npm run dev -- --host &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers running. Press Ctrl+C to stop."
echo ""

# Trap Ctrl+C to kill both servers
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup INT

# Keep script alive
wait
