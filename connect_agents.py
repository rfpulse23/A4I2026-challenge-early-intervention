import re
from pathlib import Path

server_path = Path("/config/A4I2026-challenge-early-intervention/ui/server.py")
content = server_path.read_text(encoding="utf-8")

# Ensure agent_bridge is imported
if "from agent_bridge import bridge" not in content:
    content = "from agent_bridge import bridge\n" + content

# Replace def api_chat with async def api_chat delegating to bridge.ask
new_api_chat = '''@app.post("/api/chat")
async def api_chat(payload: ChatQuery):
    """
    Connects the UI chat window directly to the live autonomous Google ADK Agent
    equipped with all 13 tools across all 3 tracks + bonus extensions.
    """
    result = await bridge.ask(query=payload.query, state_code=payload.state)
    if isinstance(result, dict) and "answer" in result:
        return result
    return {"answer": str(result)}
'''

content = re.sub(
    r'@app\.post\("/api/chat"\)\s+def api_chat\(payload: ChatQuery\):.*?(?=@app\.get\("/", response_class=HTMLResponse\))',
    new_api_chat + "\n",
    content,
    flags=re.DOTALL
)

server_path.write_text(content, encoding="utf-8")
print("Successfully connected ui/server.py to the live Google ADK agent bridge!")
