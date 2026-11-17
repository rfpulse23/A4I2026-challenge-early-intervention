import re
from pathlib import Path

server_path = Path("/config/A4I2026-challenge-early-intervention/ui/server.py")
content = server_path.read_text(encoding="utf-8")

new_api_chat = '''@app.post("/api/chat")
async def api_chat(payload: ChatQuery):
    result = await bridge.ask(query=payload.query, state_code=payload.state)
    return result
'''

content = re.sub(
    r'@app\.post\("/api/chat"\)\s+async def api_chat\(payload: ChatQuery\):.*?(?=@app\.get\("/", response_class=HTMLResponse\))',
    new_api_chat + "\n",
    content,
    flags=re.DOTALL
)

server_path.write_text(content, encoding="utf-8")
print("ui/server.py updated to return full structured question result payload!")
