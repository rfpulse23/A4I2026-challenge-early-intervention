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
      </section>
    `;
  }
}
