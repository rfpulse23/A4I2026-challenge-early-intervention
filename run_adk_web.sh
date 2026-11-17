#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================================================="
echo "  LAUNCHING GOOGLE ADK WEB INTERACTIVE AGENT UI"
echo "  Challenge 04: Agents for Impact 2026"
echo "========================================================================="

PORT=${PORT:-8080}
HOST=${HOST:-0.0.0.0}

# Kill any existing process on port $PORT to prevent Errno 98 (Address already in use)
echo "Checking and freeing port $PORT..."
fuser -k "${PORT}/tcp" 2>/dev/null || true
sleep 1

# 1. Use Google Cloud Project Vertex AI credentials
export GOOGLE_GENAI_USE_VERTEXAI=True
export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-qwiklabs-gcp-04-5956a6cfcbdf}"
export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
unset GEMINI_API_KEY

echo "Using Vertex AI with Project: $GOOGLE_CLOUD_PROJECT ($GOOGLE_CLOUD_LOCATION)"

export PYTHONPATH="/config/Desktop/AgentsForImpact/.venv/lib/python3.14/site-packages:$DIR:$PYTHONPATH"

echo "Starting ADK Web Server at http://${HOST}:${PORT} with CORS allow_origins=* ..."
echo "Serving agent from: $DIR/agent"
echo "Press Ctrl+C to terminate."

/config/Desktop/AgentsForImpact/.venv/bin/adk web --host "$HOST" --port "$PORT" --allow_origins="*" "$DIR/agent"
