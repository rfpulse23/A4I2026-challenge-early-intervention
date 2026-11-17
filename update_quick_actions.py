from pathlib import Path

p = Path("/config/A4I2026-challenge-early-intervention/ui/static/js/components/GoogleCloudAssist.js")
content = p.read_text(encoding="utf-8")

old_quick_section = '''          <!-- Quick Actions for Track 1 -->
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
          </div>'''

new_quick_section = '''          <!-- Demo Questions (Click to Ask & Update Left UI) -->
          <div class="quick-questions-section">
            <div class="quick-title">Curated Demo Questions (Live Updates Left Screen)</div>
            <div class="quick-list">
              <button class="quick-item-btn" onclick="window.app.askPrompt('Can a zero-vehicle caregiver reach the evaluation hub by public bus?')">
                <span class="material-symbols-outlined">directions_bus</span>
                <span><strong>Transit Guardrail:</strong> Can zero-vehicle caregiver reach hub by bus? (Dispatches NEMT)</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('Traverse the property graph using ISO GQL from Clarksdale Clinic.')">
                <span class="material-symbols-outlined">hub</span>
                <span><strong>Variable-Length GQL:</strong> Traverse property graph using ISO GQL syntax</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('Lock an evaluation slot with an ACID reservation token.')">
                <span class="material-symbols-outlined">lock</span>
                <span><strong>Concurrency Guardrail:</strong> Lock evaluation slot with ACID token</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('What if we switch from paper fax to e-referral across Mississippi?')">
                <span class="material-symbols-outlined">calculate</span>
                <span><strong>Query 4 Bonus:</strong> Switch from paper fax to e-referral statewide (1,098d saved)</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>

              <button class="quick-item-btn" onclick="window.app.askPrompt('Triage a 32-month-old toddler facing Part C termination cliff.')">
                <span class="material-symbols-outlined">hourglass_bottom</span>
                <span><strong>Query 5 Bonus:</strong> Triage 32-month toddler facing Part C termination</span>
                <span class="material-symbols-outlined quick-arrow">chevron_right</span>
              </button>
            </div>
          </div>'''

if old_quick_section in content:
    content = content.replace(old_quick_section, new_quick_section)
    p.write_text(content, encoding="utf-8")
    print("Successfully enriched demo question buttons in GoogleCloudAssist.js!")
else:
    print("Old quick questions block not found, check formatting.")
