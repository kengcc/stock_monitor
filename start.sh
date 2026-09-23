#!/bin/bash

cd "$(dirname "$0")"

echo "🚀 Starting Stock Monitor..."

# Kill existing process from PID file
if [ -f stock_monitor.pid ]; then
    OLD_PID=$(cat stock_monitor.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Stopping existing process (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
        # Force kill if still running
        if ps -p $OLD_PID > /dev/null 2>&1; then
            kill -9 $OLD_PID 2>/dev/null
            sleep 1
        fi
    fi
    rm -f stock_monitor.pid
fi

# Also kill any orphaned main.py processes
ORPHANS=$(pgrep -f "python.*main\.py" 2>/dev/null | grep -v $$)
if [ -n "$ORPHANS" ]; then
    echo "Killing orphaned processes: $ORPHANS"
    echo "$ORPHANS" | xargs kill 2>/dev/null
    sleep 2
fi

# Start new process
nohup venv/bin/python main.py > logs/console.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > stock_monitor.pid

echo "✅ Stock Monitor started (PID: $NEW_PID)"
echo "📝 Logs: tail -f logs/console.log"
echo "🛑 Stop: ./stop.sh"
echo ""
echo "📱 Open Telegram and chat with your bot"
echo "   Commands: /add AAPL HIGH, /priority AAPL CRITICAL, /review AAPL 2026-12-31, /list, /summary, /health"
