export class CandidateSummaryBar {
  constructor(candidate = {}) {
    this.candidate = candidate;
  }

  render() {
    const {
      name = "Mateo S.",
      age_months = 20,
      medicaid = true,
      language = "Spanish",
      primary_concern = "Developmental Concern (Screening)"
    } = this.candidate;

    return `
      <section class="candidate-strip" id="candidate-strip">
        <div class="candidate-name-box">
          <span class="material-symbols-outlined candidate-avatar-icon">account_circle</span>
          <span class="candidate-title" id="disp-candidate-name">${name}</span>
        </div>
        <div class="strip-divider"></div>
        <div class="candidate-meta-items">
          <span class="meta-item">Age: <strong>${age_months} months</strong></span>
          <div class="strip-divider"></div>
          <span class="meta-item">Medicaid: <strong>${medicaid ? 'Yes' : 'No'}</strong></span>
          <div class="strip-divider"></div>
          <span class="meta-item">Language: <strong>${language}</strong></span>
          <div class="strip-divider"></div>
          <span class="meta-item">Primary Concern: <strong>${primary_concern}</strong></span>
        </div>
      </section>
    `;
  }
}

export class AiInsightsBanner {
  constructor(insightsText = "") {
    this.insightsText = insightsText || (
      "A faster, compliant path (37 days) is available by using an eligible evaluation provider " +
      "(Eval Hub 019) instead of Intake Hub 012, which often causes delays (paper fax and eligibility mismatch)."
    );
  }

  render() {
    return `
      <section class="ai-insights-card" id="ai-insights-card">
        <div class="ai-badge-label">
          <span class="material-symbols-outlined">auto_awesome</span>
          <span>AI Insights</span>
        </div>
        <div class="strip-divider" style="height: 28px;"></div>
        <div class="ai-insights-text" id="ai-insights-content">
          ${this.insightsText}
        </div>
        <div class="ai-action-chips">
          <button class="copilot-chip" id="chip-caregiver-plan" onclick="window.app.triggerCaregiverPlan()">
            <span class="material-symbols-outlined">description</span>
            <span>Caregiver Action Plan</span>
          </button>
          <button class="copilot-chip" id="chip-lock-slot" onclick="window.app.triggerLockSlot()">
            <span class="material-symbols-outlined">lock</span>
            <span id="label-lock-slot">Lock Slot (Hub 019)</span>
          </button>
          <button class="copilot-chip" id="chip-check-transit" onclick="window.app.triggerTransitCheck()">
            <span class="material-symbols-outlined">directions_bus</span>
            <span>Check NEMT Transit</span>
          </button>
          <button class="copilot-chip chip-warn" onclick="window.app.askPrompt('Diagnose why Intake Hub 009 triggers paper-fax 3-hop bounce loops taking 76 days.')">
            <span class="material-symbols-outlined">warning</span>
            <span>Diagnose 76d Bounce Loop</span>
          </button>
        </div>
      </section>
    `;
  }
}
