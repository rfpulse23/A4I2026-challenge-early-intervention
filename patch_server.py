import re
from pathlib import Path

server_path = Path("/config/A4I2026-challenge-early-intervention/ui/server.py")
content = server_path.read_text(encoding="utf-8")

# Add import agent_bridge near the top
import_stmt = "from agent_bridge import bridge\n"
if "from agent_bridge import bridge" not in content:
    content = content.replace("from agent.tools.advanced_extensions import (", import_stmt + "from agent.tools.advanced_extensions import (")

# Replace api_chat implementation to call bridge.ask
new_api_chat = '''@app.post("/api/chat")
async def api_chat(payload: ChatQuery):
    answer = await bridge.ask(query=payload.query, state_code=payload.state)
    return {"answer": answer}
'''

content = re.sub(
    r'@app\.post\("/api/chat"\)\s+def api_chat\(payload: ChatQuery\):.*?(?=@app\.get\("/", response_class=HTMLResponse\))',
    new_api_chat + "\n",
    content,
    flags=re.DOTALL
)

server_path.write_text(content, encoding="utf-8")
print("ui/server.py updated to call live ADK Agent Bridge!")
