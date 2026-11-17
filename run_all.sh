#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================================================="
echo "  FIRST MILESTONES: IDEA PART C EARLY INTERVENTION 45-DAY TRIAGE SYSTEM"
echo "  Challenge 04: Agents for Impact 2026"
echo "========================================================================="

# 1. Activate venv if present, or use system python
if [ -f "/config/Desktop/AgentsForImpact/.venv/bin/activate" ]; then
    source /config/Desktop/AgentsForImpact/.venv/bin/activate
elif [ -f "$DIR/.venv/bin/activate" ]; then
    source "$DIR/.venv/bin/activate"
fi

echo ""
echo "=== 1. Running Hierarchical Multi-Agent Brief (Tracks 1, 2, & 3) ==="
python agent/run_hierarchical_brief.py

echo ""
echo "=== 2. Starting Interactive Triage Web Dashboard on port 8080 ==="
echo "Open your browser to: http://localhost:8080"
echo "Press Ctrl+C to stop the web server."
python ui/server.py
