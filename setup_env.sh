#!/usr/bin/env bash
set -e

echo "=== 1. Creating Python Virtual Environment ==="
if [ ! -d ".venv" ]; then
  python3 -m venv --system-site-packages .venv
fi

echo "=== 2. Configuring site-packages links ==="
SITE_PACKAGES=$(find .venv/lib -name site-packages -type d | head -n 1)
echo "/opt/venv/lib/python3.14/site-packages" > "${SITE_PACKAGES}/opt_venv.pth"

echo "=== 3. Installing dependencies (MCP, FastMCP, etc.) ==="
.venv/bin/pip install "mcp<2" fastmcp

echo "=== 4. Creating .env template ==="
if [ ! -f ".env" ]; then
  cat << 'ENV_EOF' > .env
# Gemini API Key (Get from https://aistudio.google.com/app/api-keys)
GEMINI_API_KEY=your_gemini_api_key_here
# Optional: Model selection
GEMINI_MODEL=gemini-2.5-flash
ENV_EOF
  echo "Created .env file. Please update your GEMINI_API_KEY in .env."
else
  echo ".env file already exists."
fi

echo "=== 5. Testing environment setup ==="
.venv/bin/python -c "
import google.adk as adk
from google.adk.tools import McpToolset
import fastmcp
print('Environment verification passed!')
print(f'ADK Version: {adk.__version__}')
"

echo "=== Setup Complete! ==="
echo "To activate environment: source .venv/bin/activate"
