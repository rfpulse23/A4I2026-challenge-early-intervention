export class PathwayComparison {
  constructor(data = {}) {
    this.data = data;
  }

  render() {
    const rec = this.data.recommended_path || {};
    const hist = this.data.usual_path || {};

    const recSteps = rec.stepper_nodes || [];
    const recRows = rec.table_rows || [];

    const histSteps = hist.stepper_nodes || [];
    const histRows = hist.table_rows || [];

    const recTotal = rec.estimated_total_days || 37;
    const histTotal = hist.estimated_total_days || 76;

    return `
      <section class="pathway-section">
        <h2 class="section-heading">Pathway Comparison</h2>

        <!-- Recommended Path (AI) -->
        <div class="pathway-card" id="card-recommended">
          <div class="pathway-header open" id="header-rec" onclick="window.app.toggleAccordion('rec')">
            <div class="pathway-title-area">
              <span class="material-symbols-outlined" id="arrow-rec" style="font-size: 20px;">expand_more</span>
              <span class="pathway-type-title title-recommended">1. Recommended Path (AI)</span>
              <span class="pill-badge pill-within-limit">Within 45-day limit</span>
              <span class="app-divider" style="height: 14px;"></span>
              <span class="pathway-days-summary">Estimated total: <strong class="days-stat-number days-green">${recTotal} days</strong></span>
            </div>
          </div>
          
          <div class="pathway-body" id="body-rec">
            <!-- Stepper Flow -->
            <div class="stepper-flow">
              ${recSteps.map((s, idx) => `
                <div class="flow-step-node node-recommended">
                  <div class="node-role">${s.role || s.title}</div>
                  <div class="node-provider-name">${s.provider || ''}</div>
                  <div class="node-days">(${s.days_label})</div>
                </div>
                ${idx < recSteps.length - 1 ? '<div class="flow-arrow"><span class="material-symbols-outlined">arrow_forward</span></div>' : ''}
              `).join('')}
            </div>

            <!-- Table -->
            <div class="details-subheading">Pathway details</div>
            <div class="details-table-wrap">
              <table class="details-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Step & Provider</th>
                    <th>Channel</th>
                    <th>Wait Days</th>
                    <th>Cumulative</th>
                    <th>Key Notes</th>
                  </tr>
                </thead>
                <tbody>
                  ${recRows.map(r => `
                    <tr>
                      <td>${r.step_no}</td>
                      <td><strong>${r.step_name}</strong></td>
                      <td>${r.channel}</td>
                      <td>${r.wait_days}</td>
                      <td>${r.cumulative}</td>
                      <td>${r.notes}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Usual Path (Historical) -->
        <div class="pathway-card" id="card-usual">
          <div class="pathway-header" id="header-usual" onclick="window.app.toggleAccordion('usual')">
            <div class="pathway-title-area">
              <span class="material-symbols-outlined" id="arrow-usual" style="font-size: 20px;">chevron_right</span>
              <span class="pathway-type-title title-usual">2. Usual Path (Historical)</span>
              <span class="pill-badge pill-over-limit">Over 45-day limit</span>
              <span class="app-divider" style="height: 14px;"></span>
              <span class="pathway-days-summary">Estimated total: <strong class="days-stat-number days-red">${histTotal} days</strong></span>
            </div>
          </div>

          <div class="pathway-body" id="body-usual" style="display: none;">
            <!-- Stepper Flow -->
            <div class="stepper-flow">
              ${histSteps.map((s, idx) => `
                <div class="flow-step-node ${s.is_returned ? 'node-returned' : ''}">
                  <div class="node-role ${s.is_returned ? 'text-returned' : ''}">${s.is_returned ? "''" + (s.role || s.title) + "''" : (s.role || s.title)}</div>
                  <div class="node-provider-name ${s.is_returned ? 'text-returned-sub' : ''}">${s.provider || ''}</div>
                  <div class="node-days ${s.is_returned ? 'node-days-returned' : ''}">${s.days_label.startsWith('+') ? s.days_label : '(' + s.days_label + ')'}</div>
                </div>
                ${idx < histSteps.length - 1 ? '<div class="flow-arrow"><span class="material-symbols-outlined">arrow_forward</span></div>' : ''}
              `).join('')}
            </div>

            <!-- Table -->
            <div class="details-subheading">Historical Handoff Breakdown</div>
            <div class="details-table-wrap">
              <table class="details-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Step & Provider</th>
                    <th>Channel</th>
                    <th>Wait Days</th>
                    <th>Cumulative</th>
                    <th>Key Notes</th>
                  </tr>
                </thead>
                <tbody>
                  ${histRows.map(r => `
                    <tr>
                      <td>${r.step_no}</td>
                      <td><strong>${r.step_name}</strong></td>
                      <td>${r.channel}</td>
                      <td>${r.wait_days}</td>
                      <td>${r.cumulative}</td>
                      <td>${r.notes}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </section>
    `;
  }
}
