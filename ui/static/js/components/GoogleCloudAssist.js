export class GoogleCloudAssist {
  constructor(messages = []) {
    this.messages = messages.length > 0 ? messages : [
      {
        sender: "user",
        text: "Why does Intake Hub 012 look healthy but still cause 45-day breaches?"
      },
      {
        sender: "ai",
        text: "Intake Hub 012 has a short internal wait (median 5–6 days), so it looks healthy on a spreadsheet. But 28% of similar cases are re-routed due to paper fax and eligibility mismatches, adding ~11 extra days and often pushing the total over 45 days."
      }
    ];
  }

  render() {
    return `
      <aside class="assist-card">
        <div class="assist-header">
          <div class="assist-brand">
            <span class="material-symbols-outlined">auto_awesome</span>
            <span>Google Cloud Assist</span>
          </div>
          <span class="adk-badge">Conversational ADK Agent</span>
        </div>

        <div class="assist-scroll-content" id="assist-chat-history">
          <!-- Chat Bubbles -->
          ${this.messages.map(m => `
            <div class="chat-msg ${m.sender}">
              <div class="chat-avatar ${m.sender === 'user' ? 'user-avatar' : 'ai-avatar'}">
                <span class="material-symbols-outlined">${m.sender === 'user' ? 'person' : 'auto_awesome'}</span>
              </div>
              <div class="chat-bubble">
                ${m.text}
              </div>
            </div>
          `).join('')}

          <!-- Try Asking Me -->
          <div class="quick-questions-section">
            <div class="quick-title">Try asking me...</div>
            <div class="quick-list">
              <button class="quick-item-btn" onclick="window.app.askPrompt('Trace the 3–4 hop referral chains that breached 45 days.')">
                <span class="material-symbols-outlined">hub</span>
                <span>Trace the 3–4 hop referral chains that breached 45 days.</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('What if we switch from paper fax to e-referral?')">
                <span class="material-symbols-outlined">swap_horiz</span>
                <span>What if we switch from paper fax to e-referral?</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('Which intake hub saves the most delayed child-days?')">
                <span class="material-symbols-outlined">bar_chart</span>
                <span>Which intake hub saves the most delayed child-days?</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('Which neighborhoods have the most breaches?')">
                <span class="material-symbols-outlined">location_on</span>
                <span>Which neighborhoods have the most breaches?</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('Write a caregiver action note (English & Spanish).')">
                <span class="material-symbols-outlined">description</span>
                <span>Write a caregiver action note (English & Spanish).</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Input Bar -->
        <div class="assist-input-bar">
          <input type="text" class="assist-input" id="assist-input-field" placeholder="Ask a follow-up question..." />
          <button class="send-btn" id="btn-send-chat" title="Send">
            <span class="material-symbols-outlined">send</span>
          </button>
        </div>
      </aside>
    `;
  }
}
