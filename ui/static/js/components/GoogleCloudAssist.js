export class GoogleCloudAssist {
  constructor(messages = [], activeTrack = "new_case") {
    this.messages = messages.length > 0 ? messages : [
      {
        sender: "user",
        text: "How does the assistant coordinate all 3 IDEA Part C tracks under the federal 45-day clock?"
      },
      {
        sender: "ai",
        text: "Welcome! Our assistant coordinates across all 3 tracks:\n• Track 1: Routes 20-month toddlers like Mateo S. to bilingual Medicaid evaluators under 45 days.\n• Track 2: Audits regional networks, exposing 3-hop paper-fax bounce hubs.\n• Track 3: Prioritizes high-poverty zero-vehicle tracts for community screening only when downstream <=45-day capacity is strictly verified."
      }
    ];
    this.activeTrack = activeTrack;
  }

  render() {
    let quickQuestions = [];

    if (this.activeTrack === "new_case") {
      quickQuestions = [
        {
          icon: "route",
          text: "Traverse the property graph using ISO GQL from Clarksdale Clinic.",
          prompt: "Traverse the BigQuery property graph using variable-length ISO GQL from Clarksdale Clinic to find an active compliant pathway matching Medicaid and bilingual requirements."
        },
        {
          icon: "directions_bus",
          text: "Can a zero-vehicle caregiver reach the evaluation hub by public bus?",
          prompt: "Can a zero-vehicle caregiver reach the evaluation hub by public bus?"
        },
        {
          icon: "lock",
          text: "Lock an evaluation slot with an ACID reservation token.",
          prompt: "Display the complete 4-hop pathway latency breakdown for CHAIN-MS-009, lock an evaluation slot with an ACID reservation, and defend your choice of the ADK Web interface."
        },
        {
          icon: "description",
          text: "Generate a bilingual caregiver action note (English & Spanish).",
          prompt: "Write a caregiver action note (English & Spanish)."
        }
      ];
    } else if (this.activeTrack === "network_audit") {
      quickQuestions = [
        {
          icon: "hub",
          text: "Diagnose why regional 45-day compliance dropped below 60%.",
          prompt: "Trace the 3–4 hop referral chains that breached 45 days and identify top bounce hubs."
        },
        {
          icon: "swap_horiz",
          text: "Run Query 4 counterfactual simulation (paper fax -> EHR portal).",
          prompt: "What if we switch from paper fax to e-referral across Mississippi?"
        },
        {
          icon: "bar_chart",
          text: "Which intake hub saves the most delayed child-days?",
          prompt: "Which intake hub saves the most delayed child-days?"
        },
        {
          icon: "timer",
          text: "Triage a 32-month-old toddler approaching the age-3 cliff.",
          prompt: "Triage a 32-month-old toddler facing Part C termination."
        }
      ];
    } else {
      quickQuestions = [
        {
          icon: "location_on",
          text: "Prioritize top high-poverty, zero-vehicle tracts with verified capacity.",
          prompt: "Plan the community screening season prioritizing tracts with verified downstream capacity."
        },
        {
          icon: "verified_user",
          text: "How do we prevent creating dead-end waitlists during screening?",
          prompt: "Why must downstream 45-day evaluation capacity be verified before screening?"
        },
        {
          icon: "storefront",
          text: "Locate partner Head Start and WIC centers for mobile vans.",
          prompt: "Find Head Start and WIC screening sites in high-need counties."
        },
        {
          icon: "directions_bus",
          text: "Check transit feasibility for high-need Delta tracts.",
          prompt: "Can a zero-vehicle caregiver reach the evaluation hub by public bus?"
        }
      ];
    }

    return `
      <aside class="assist-card">
        <div class="assist-header">
          <div class="assist-brand">
            <span class="material-symbols-outlined">auto_awesome</span>
            <span>Google Cloud Assist</span>
          </div>
          <span class="adk-badge">Live ADK Agent</span>
        </div>

        <div class="assist-scroll-content" id="assist-chat-history">
          <!-- Chat Bubbles -->
          ${this.messages.map(m => `
            <div class="chat-msg ${m.sender}">
              <div class="chat-avatar ${m.sender === 'user' ? 'user-avatar' : 'ai-avatar'}">
                <span class="material-symbols-outlined">${m.sender === 'user' ? 'person' : 'auto_awesome'}</span>
              </div>
              <div class="chat-bubble">
                ${m.text.replace(/\n/g, '<br/>')}
              </div>
            </div>
          `).join('')}

          <!-- Try Asking Me -->
          <div class="quick-questions-section">
            <div class="quick-title">Quick Actions for this Track...</div>
            <div class="quick-list">
              ${quickQuestions.map((q, idx) => `
                <button class="quick-item-btn" data-prompt-idx="${idx}" onclick="window.app.askPrompt(this.getAttribute('data-prompt'))" data-prompt="${q.prompt.replace(/"/g, '&quot;')}">
                  <span class="material-symbols-outlined">${q.icon}</span>
                  <span>${q.text}</span>
                  <span class="material-symbols-outlined quick-arrow">chevron_right</span>
                </button>
              `).join('')}
            </div>
          </div>
        </div>

        <!-- Input Bar -->
        <div class="assist-input-bar">
          <input type="text" class="assist-input" id="assist-input-field" placeholder="Ask a question about this track..." autocomplete="off" />
          <button class="send-btn" id="btn-send-chat" title="Send">
            <span class="material-symbols-outlined">send</span>
          </button>
        </div>
      </aside>
    `;
  }
}
