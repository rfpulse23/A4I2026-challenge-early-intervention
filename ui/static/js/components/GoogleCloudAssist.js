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
          text: "Traverse property graph with ISO GQL",
          prompt: "Traverse the BigQuery property graph using variable-length ISO GQL from Clarksdale Clinic to find an active compliant pathway matching Medicaid and bilingual requirements."
        },
        {
          icon: "directions_bus",
          text: "Can a zero-vehicle caregiver reach hub?",
          prompt: "Can a zero-vehicle caregiver reach the evaluation hub by public bus?"
        },
        {
          icon: "lock",
          text: "Lock evaluation slot with ACID token",
          prompt: "Display the complete 4-hop pathway latency breakdown for CHAIN-MS-009, lock an evaluation slot with an ACID reservation, and defend your choice of the ADK Web interface."
        },
        {
          icon: "description",
          text: "Generate bilingual caregiver note",
          prompt: "Write a caregiver action note (English & Spanish)."
        }
      ];
    } else if (this.activeTrack === "network_audit") {
      quickQuestions = [
        {
          icon: "hub",
          text: "Diagnose compliance drop below 60%",
          prompt: "Trace the 3–4 hop referral chains that breached 45 days and identify top bounce hubs."
        },
        {
          icon: "swap_horiz",
          text: "Run Q4 counterfactual simulation",
          prompt: "What if we switch from paper fax to e-referral across Mississippi?"
        },
        {
          icon: "bar_chart",
          text: "Which intake hub saves most days?",
          prompt: "Which intake hub saves the most delayed child-days?"
        },
        {
          icon: "timer",
          text: "Triage 32-month aging-out cliff",
          prompt: "Triage a 32-month-old toddler facing Part C termination."
        }
      ];
    } else {
      quickQuestions = [
        {
          icon: "location_on",
          text: "Prioritize top tracts with verified capacity",
          prompt: "Plan the community screening season prioritizing tracts with verified downstream capacity."
        },
        {
          icon: "verified_user",
          text: "Prevent creating dead-end waitlists",
          prompt: "Why must downstream 45-day evaluation capacity be verified before screening?"
        },
        {
          icon: "storefront",
          text: "Locate Head Start and WIC centers",
          prompt: "Find Head Start and WIC screening sites in high-need counties."
        },
        {
          icon: "directions_bus",
          text: "Check Delta transit feasibility",
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

        <!-- Chat Stream (Takes Full Height with Auto-Scroll) -->
        <div class="assist-scroll-content" id="assist-chat-history">
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
        </div>

        <!-- Compact Collapsible Quick Chips Section (Fixed at bottom above input) -->
        <div class="assist-quick-chips-wrapper">
          <div class="quick-chips-header" onclick="window.app.toggleQuickChips()">
            <span class="quick-title"><span class="material-symbols-outlined" style="font-size:14px; vertical-align:middle;">flash_on</span> Suggested Actions</span>
            <span class="material-symbols-outlined quick-chips-toggle-icon" id="quick-chips-toggle-icon">expand_less</span>
          </div>
          <div class="quick-chips-scroll" id="quick-chips-container">
            ${quickQuestions.map((q, idx) => `
              <button class="quick-chip-btn" data-prompt-idx="${idx}" onclick="window.app.askPrompt(this.getAttribute('data-prompt'))" data-prompt="${q.prompt.replace(/"/g, '&quot;')}" title="${q.prompt.replace(/"/g, '&quot;')}">
                <span class="material-symbols-outlined">${q.icon}</span>
                <span>${q.text}</span>
              </button>
            `).join('')}
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
