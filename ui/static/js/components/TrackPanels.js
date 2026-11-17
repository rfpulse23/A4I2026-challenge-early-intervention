/**
 * TrackPanels.js
 * Dedicated UI components for Track 2 (Network Audit) and Track 3 (Community Screening Season).
 */

export class NetworkAuditPanel {
  constructor(auditData = {}) {
    this.data = auditData;
  }

  render() {
    const bn = this.data.bottlenecks || {};
    const agency = bn.lead_agency_status || {};
    const hubs = bn.top_regional_bounce_hubs || [];
    const q4 = this.data.statewide_paper_fax_remediation || {};

    return `
      <section class="pathway-section track-audit-panel">
        <div class="track-header-banner">
          <div class="track-tag"><span class="material-symbols-outlined">hub</span> Track 2: Network Audit</div>
          <h2>This Quarter's Network Audit & Bottleneck Remediation</h2>
          <p class="track-desc">Investigate why 45-day timely IFSP compliance dropped below 60% and remediate systemic paper-fax intake links.</p>
        </div>

        <!-- Metric Cards Grid -->
        <div class="metrics-grid">
          <div class="metric-card alert">
            <div class="metric-label">Regional Compliance</div>
            <div class="metric-value">${agency.statutory_compliance_pct || 52.5}%</div>
            <div class="metric-subtext">Federal SLA: >= 60.0% (BREACHED)</div>
          </div>
          <div class="metric-card success">
            <div class="metric-label">Q4 Counterfactual Recovery</div>
            <div class="metric-value">100%</div>
            <div class="metric-subtext">${q4.cases_recovered_to_compliance || 26} of ${q4.baseline_breaches || 26} cases recovered</div>
          </div>
          <div class="metric-card highlight">
            <div class="metric-label">Child-Days Saved</div>
            <div class="metric-value">${q4.total_child_days_saved || 1098}</div>
            <div class="metric-subtext">By replacing paper fax with EHR portal</div>
          </div>
        </div>

        <!-- Deceptive Hubs Table -->
        <div class="details-subheading" style="margin-top:20px;">Top Systemic Bounce Hubs (Spreadsheet Trap)</div>
        <div class="details-table-wrap">
          <table class="details-table">
            <thead>
              <tr>
                <th>Provider ID</th>
                <th>Intake Coordinator Hub</th>
                <th>Internal Wait</th>
                <th>Breached Chains</th>
                <th>Downstream Delay Caused</th>
                <th>Root Cause Diagnosis</th>
              </tr>
            </thead>
            <tbody>
              ${hubs.map(h => `
                <tr>
                  <td><code>${h.provider_id}</code></td>
                  <td><strong>${h.organization_name}</strong></td>
                  <td><span class="pill-badge pill-within-limit">${h.deceptive_internal_wait_days} days (Deceptive)</span></td>
                  <td><strong style="color:var(--md-error);">${h.breached_chains_passing_through} chains</strong></td>
                  <td><strong>${h.downstream_wait_days_caused} child-days</strong></td>
                  <td>${h.root_cause}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Action Card -->
        <div class="recommendation-callout" style="margin-top:16px;">
          <span class="material-symbols-outlined" style="color:var(--md-primary); font-size:24px;">bolt</span>
          <div>
            <strong>Recommended Policy Action:</strong> Mandate electronic EHR portal integration for Provider <code>SYN-PROV-MS-009</code>. This single node fix recovers compliance to 65.9% and saves 537 delayed child-days in Bolivar and Sunflower counties.
          </div>
        </div>
      </section>
    `;
  }
}

export class ScreeningSeasonPanel {
  constructor(seasonData = {}) {
    this.data = seasonData;
  }

  render() {
    const plan = this.data.screening_plan || {};
    const tracts = plan.priority_screening_tracts || [];
    const byod = this.data.byod_enrichment || {};

    return `
      <section class="pathway-section track-screening-panel">
        <div class="track-header-banner">
          <div class="track-tag"><span class="material-symbols-outlined">event_available</span> Track 3: Screening Season</div>
          <h2>This Community Screening Season: Verified Capacity Triage</h2>
          <p class="track-desc">Prioritize under-5 high-poverty, zero-vehicle tracts strictly verifying downstream &lt;=45-day capacity before screening.</p>
        </div>

        <!-- Guardrail Banner -->
        <div class="guardrail-callout">
          <span class="material-symbols-outlined" style="color:#0f5223; font-size:22px;">verified_user</span>
          <div>
            <strong>Downstream &lt;=45-Day Capacity Guardrail:</strong> Screening toddlers without verifying an active evaluation pathway creates dead-end waitlists. All approved sites below have verified evaluation hub capacity &lt;=20 days.
          </div>
        </div>

        <!-- Priority Tracts Table -->
        <div class="details-subheading" style="margin-top:20px;">Prioritized Census Tracts for Mobile Screening Vans</div>
        <div class="details-table-wrap">
          <table class="details-table">
            <thead>
              <tr>
                <th>Census Tract GeoID</th>
                <th>County</th>
                <th>Under-5 Poverty</th>
                <th>Zero-Vehicle %</th>
                <th>Nearest Eval Hub</th>
                <th>Travel Dist</th>
                <th>Hub Wait</th>
                <th>Action Recommendation</th>
              </tr>
            </thead>
            <tbody>
              ${tracts.map(t => `
                <tr>
                  <td><code>${t.census_tract_geoid}</code></td>
                  <td><strong>${t.county_name}</strong></td>
                  <td><span class="pill-badge pill-over-limit">${t.under_5_poverty_rate_pct}%</span></td>
                  <td>${t.zero_vehicle_household_pct}%</td>
                  <td>${t.closest_downstream_eval_hub}</td>
                  <td>${t.distance_to_eval_hub_km} km</td>
                  <td><strong>${t.downstream_hub_wait_days} days</strong></td>
                  <td>
                    <span class="pill-badge ${t.screening_season_action.includes('MANDATORY') ? 'pill-over-limit' : 'pill-within-limit'}">
                      ${t.screening_season_action}
                    </span>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Partner Locations Section -->
        <div class="recommendation-callout" style="margin-top:16px;">
          <span class="material-symbols-outlined" style="color:var(--md-primary); font-size:24px;">storefront</span>
          <div>
            <strong>Compliant BYOD Co-Locations:</strong> Deploy mobile screening teams directly to licensed <strong>Head Start Centers</strong> and <strong>WIC Clinics</strong> in Coahoma and Leflore counties, automatically dispatching Medicaid NEMT shuttles for zero-vehicle households.
          </div>
        </div>
      </section>
    `;
  }
}
