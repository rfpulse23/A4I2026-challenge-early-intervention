export class FilterBar {
  constructor(candidates = [], selectedCandidate = "Mateo S.", selectedState = "MS") {
    this.candidates = candidates;
    this.selectedCandidate = selectedCandidate;
    this.selectedState = selectedState;
  }

  render() {
    return `
      <section class="filter-bar">
        <div class="filter-group">
          <label class="filter-label">Planning before referral</label>
          <div class="filter-input-wrap">
            <select class="filter-select" id="select-task-mode">
              <option value="new_case">Plan a Referral Path (New Case)</option>
              <option value="network_audit">Quarterly Network Audit (Track 2)</option>
              <option value="screening_season">Community Screening Season (Track 3)</option>
            </select>
            <span class="material-symbols-outlined input-icon-right" style="pointer-events:none;">expand_more</span>
          </div>
        </div>

        <div class="filter-group">
          <label class="filter-label">Region</label>
          <div class="filter-input-wrap">
            <select class="filter-select" id="select-region">
              <option value="MS" ${this.selectedState === 'MS' ? 'selected' : ''}>Mississippi (MS)</option>
              <option value="AL" ${this.selectedState === 'AL' ? 'selected' : ''}>Alabama (AL)</option>
              <option value="GA" ${this.selectedState === 'GA' ? 'selected' : ''}>Georgia (GA)</option>
              <option value="TX" ${this.selectedState === 'TX' ? 'selected' : ''}>Texas (TX)</option>
              <option value="CA" ${this.selectedState === 'CA' ? 'selected' : ''}>California (CA)</option>
              <option value="NY" ${this.selectedState === 'NY' ? 'selected' : ''}>New York (NY)</option>
            </select>
            <span class="material-symbols-outlined input-icon-right" style="pointer-events:none;">expand_more</span>
          </div>
        </div>

        <div class="filter-group">
          <label class="filter-label">Candidate Name</label>
          <div class="filter-input-wrap">
            <span class="material-symbols-outlined input-icon-left">search</span>
            <input type="text" class="filter-input" id="input-candidate" value="${this.selectedCandidate}" placeholder="Search candidate..." />
            <span class="material-symbols-outlined input-icon-right" id="clear-candidate-btn">close</span>
          </div>
        </div>

        <button class="btn-primary-action" id="btn-analyze-pathways">
          <span class="material-symbols-outlined" style="font-size: 18px;">auto_awesome</span>
          <span>Analyze Pathways</span>
        </button>
      </section>
    `;
  }
}
