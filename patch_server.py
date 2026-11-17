import re
from pathlib import Path

p = Path("/config/A4I2026-challenge-early-intervention/ui/server.py")
content = p.read_text(encoding="utf-8")

old_code = '''@app.post("/api/chat")
async def api_chat(payload: ChatQuery):
    """
    Connects the UI chat window directly to the live autonomous Google ADK Agent
    equipped with all 13 tools across all 3 tracks + bonus extensions.
    """
    result = await bridge.ask(query=payload.query, state_code=payload.state)
    if isinstance(result, dict) and "answer" in result:
        return result
    return {"answer": str(result)}'''

new_code = '''@app.post("/api/chat")
async def api_chat(payload: ChatQuery):
    """
    Connects the UI chat window directly to the live autonomous Google ADK Agent
    and returns both the agent answer and dynamic UI update for the left side of the dashboard.
    """
    result = await bridge.ask(query=payload.query, state_code=payload.state)
    if isinstance(result, dict):
        return {
            "answer": result.get("answer", ""),
            "ui_update": result.get("ui_update", None)
        }
    return {"answer": str(result), "ui_update": None}'''

if old_code in content:
    content = content.replace(old_code, new_code)
    p.write_text(content, encoding="utf-8")
    print("Successfully patched ui/server.py api_chat to return ui_update!")
else:
    print("Could not find exact old_code block in ui/server.py, applying regex replacement...")
    content = re.sub(
        r'@app\.post\("/api/chat"\)\s+async def api_chat\(payload: ChatQuery\):.*?(?=@app\.get\("/", response_class=HTMLResponse\))',
        new_code + "\n\n",
        content,
        flags=re.DOTALL
    )
    p.write_text(content, encoding="utf-8")
    print("Applied regex replacement in ui/server.py!")
