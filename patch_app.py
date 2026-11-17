from pathlib import Path

app_path = Path("/config/A4I2026-challenge-early-intervention/ui/static/js/app.js")
content = app_path.read_text(encoding="utf-8")

old_ask = '''  async askPrompt(promptText) {
    this.chatMessages.push({ sender: "user", text: promptText });
    this.updateChatUI();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: promptText, state: this.currentState })
      });
      const data = await res.json();
      this.chatMessages.push({ sender: "ai", text: data.answer });
      this.updateChatUI();
    } catch (e) {
      this.chatMessages.push({ sender: "ai", text: "Error connecting to ADK Agent." });
      this.updateChatUI();
    }
  }'''

new_ask = '''  async askPrompt(promptText) {
    if (!promptText || !promptText.trim()) return;
    this.chatMessages.push({ sender: "user", text: promptText.trim() });
    this.chatMessages.push({ sender: "ai", text: "Analyzing across BigQuery & Property Graph..." });
    this.updateChatUI();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: promptText.trim(), state: this.currentState })
      });
      const data = await res.json();
      this.chatMessages.pop(); // remove loading indicator
      this.chatMessages.push({ sender: "ai", text: data.answer || "No response received." });
    } catch (e) {
      this.chatMessages.pop();
      this.chatMessages.push({ sender: "ai", text: "Error connecting to backend ADK Agent." });
    } finally {
      this.updateChatUI();
    }
  }'''

if old_ask in content:
    content = content.replace(old_ask, new_ask)
    app_path.write_text(content, encoding="utf-8")
    print("Updated askPrompt in app.js with live loading indicator!")
else:
    print("Pattern not found, skipping direct replacement")
