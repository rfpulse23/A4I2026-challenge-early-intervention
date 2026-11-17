from pathlib import Path

p = Path("/config/A4I2026-challenge-early-intervention/ui/static/js/app.js")
content = p.read_text(encoding="utf-8")

old_ask_block = '''    try {
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
    }'''

new_ask_block = '''    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: promptText.trim(), state: this.currentState })
      });
      const data = await res.json();
      this.chatMessages.pop(); // remove loading indicator
      this.chatMessages.push({ sender: "ai", text: data.answer || "No response received." });

      // Dynamically update the LEFT SIDE of the dashboard based on the agent answer
      if (data.ui_update) {
        this.applyLeftUiUpdate(data.ui_update);
      }
    } catch (e) {
      this.chatMessages.pop();
      this.chatMessages.push({ sender: "ai", text: "Error connecting to backend ADK Agent." });
    } finally {
      this.updateChatUI();
    }'''

extra_methods = '''
  applyLeftUiUpdate(uiUpdate) {
    // 1. Update AI Insights Banner
    if (uiUpdate.insights) {
      const bannerText = document.querySelector(".ai-banner-text");
      if (bannerText) bannerText.textContent = uiUpdate.insights;
    }

    // 2. Update Recommended Path (AI Stepper & Table)
    if (uiUpdate.recommended_path) {
      this.pathwayData.recommended_path = {
        ...this.pathwayData.recommended_path,
        ...uiUpdate.recommended_path
      };
      
      const leftCol = document.querySelector(".left-col");
      if (leftCol) {
        const candidateSummary = new CandidateSummaryBar(this.candidateData);
        const aiInsights = new AiInsightsBanner(uiUpdate.insights || this.pathwayData.insights);
        const pathwayComp = new PathwayComparison(this.pathwayData);

        leftCol.innerHTML = `
          ${candidateSummary.render()}
          ${aiInsights.render()}
          ${pathwayComp.render()}
        `;
      }
    }
  }
'''

if old_ask_block in content:
    content = content.replace(old_ask_block, new_ask_block)
    # Insert extra method before window.app = new App();
    content = content.replace("  updateChatUI() {", extra_methods + "\n  updateChatUI() {")
    p.write_text(content, encoding="utf-8")
    print("Successfully updated app.js to update the left side of the UI based on answers!")
else:
    print("Pattern not found in app.js!")
