#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PORT=${PORT:-8080}
HOST=${HOST:-0.0.0.0}

echo "========================================================================="
echo "  LAUNCHING EARLY INTERVENTION 3-TRACK DASHBOARD & ASSISTANT"
echo "  Challenge 04: Agents for Impact 2026"
echo "========================================================================="

# Free port if occupied
fuser -k "${PORT}/tcp" 2>/dev/null || true
sleep 1

export PYTHONPATH="$DIR:$PYTHONPATH"

echo "Starting UI Server at http://${HOST}:${PORT} ..."
echo "Serving Tracks 1, 2, and 3 from: $DIR/ui"
echo "Press Ctrl+C to terminate."

/config/Desktop/AgentsForImpact/.venv/bin/python -m uvicorn ui.server:app --host "$HOST" --port "$PORT" --reload
