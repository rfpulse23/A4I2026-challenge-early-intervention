export class FilterBar {
  constructor(candidates = [], selectedCandidate = "Mateo S.", selectedState = "MS", selectedTrack = "new_case") {
    this.candidates = candidates;
    this.selectedCandidate = selectedCandidate;
    this.selectedState = selectedState;
    this.selectedTrack = selectedTrack;
  }

  render() {
    return `
      <section class="filter-bar">
        <div class="filter-group">
          <label class="filter-label">Challenge Track & Role</label>
          <div class="filter-input-wrap">
            <select class="filter-select" id="select-task-mode">
              <option value="new_case" ${this.selectedTrack === 'new_case' ? 'selected' : ''}>🧭 Track 1: Today's Toddler Referral</option>
              <option value="network_audit" ${this.selectedTrack === 'network_audit' ? 'selected' : ''}>🕸️ Track 2: This Quarter's Network Audit</option>
              <option value="screening_season" ${this.selectedTrack === 'screening_season' ? 'selected' : ''}>📋 Track 3: This Community Screening Season</option>
            </select>
            <span class="material-symbols-outlined input-icon-right" style="pointer-events:none;">expand_more</span>
          </div>
        </div>

        <div class="filter-group">
          <label class="filter-label">State Jurisdiction</label>
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

        <div class="filter-group" style="${this.selectedTrack !== 'new_case' ? 'opacity: 0.5; pointer-events: none;' : ''}">
          <label class="filter-label">Candidate Name</label>
          <div class="filter-input-wrap">
            <span class="material-symbols-outlined input-icon-left">search</span>
            <input type="text" class="filter-input" id="input-candidate" value="${this.selectedCandidate}" placeholder="Search candidate..." />
            <span class="material-symbols-outlined input-icon-right" id="clear-candidate-btn">close</span>
          </div>
        </div>

        <button class="btn-primary-action" id="btn-analyze-pathways">
          <span class="material-symbols-outlined" style="font-size: 18px;">auto_awesome</span>
          <span>Run Analysis</span>
        </button>
      </section>
    `;
  }
}
