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

          <!-- Quick Actions for Track 1 -->
          <div class="quick-questions-section">
            <div class="quick-title">Quick Actions for this Track...</div>
            <div class="quick-list">
              <button class="quick-item-btn" onclick="window.app.askPrompt('Traverse the property graph using ISO GQL from Clarksdale Clinic.')">
                <span class="material-symbols-outlined">hub</span>
                <span>Traverse the property graph using ISO GQL from Clarksdale Clinic.</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('Can a zero-vehicle caregiver reach the evaluation hub by public bus?')">
                <span class="material-symbols-outlined">directions_bus</span>
                <span>Can a zero-vehicle caregiver reach the evaluation hub by public bus?</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('Lock an evaluation slot with an ACID reservation token.')">
                <span class="material-symbols-outlined">lock</span>
                <span>Lock an evaluation slot with an ACID reservation token.</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('Generate a bilingual caregiver action note (English & Spanish).')">
                <span class="material-symbols-outlined">description</span>
                <span>Generate a bilingual caregiver action note (English & Spanish).</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>
            </div>
          </div>
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
