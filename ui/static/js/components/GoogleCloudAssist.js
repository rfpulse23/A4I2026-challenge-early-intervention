export class GoogleCloudAssist {
  constructor(messages = []) {
    this.messages = messages.length > 0 ? messages : [
      {
        sender: "user",
        text: "How does the assistant coordinate Track 1 referrals under the federal 45-day clock?"
      },
      {
        sender: "ai",
        text: "Focusing on Track 1: Active Toddler Referral. For 20-month-old Mateo S. in Bolivar County, our system traverses BigQuery referral graphs to avoid paper-fax bounce loops (e.g. at Hub 009) and connects him directly to a verified bilingual Medicaid evaluation hub within 22 calendar days (well under the 45-day federal clock)."
      }
    ];
  }

  render() {
    return `
      <aside class="assist-card">
        <div class="assist-header">
          <div class="assist-brand">
            <span class="material-symbols-outlined">auto_awesome</span>
            <span>Early Intervention Co-Pilot</span>
          </div>
          <span class="adk-badge">45-Day Statutory Triage</span>
        </div>

        <div class="assist-scroll-content" id="assist-chat-history">
          <!-- Chat Bubbles Only: Zero obstruction, full scroll area -->
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
        </div>

        <!-- Input Bar -->
        <div class="assist-input-bar">
          <input type="text" class="assist-input" id="assist-input-field" placeholder="Ask a question about this track..." />
          <button class="send-btn" id="btn-send-chat" title="Send">
            <span class="material-symbols-outlined">send</span>
          </button>
        </div>
      </aside>
    `;
  }
}
