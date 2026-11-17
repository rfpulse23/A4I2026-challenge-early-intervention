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
          <label class="filter-label">Challenge Track & Role</label>
          <div class="filter-input-wrap">
            <select class="filter-select" id="select-task-mode">
              <option value="new_case">Track 1: Today's Toddler Referral</option>
              <option value="network_audit">Track 2: Quarterly Network Audit</option>
              <option value="screening_season">Track 3: Community Screening Season</option>
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

        <div class="filter-group">
          <label class="filter-label">Active Candidate Referral</label>
          <div class="filter-input-wrap">
            <select class="filter-select" id="select-candidate-dropdown" style="min-width: 250px;">
              <option value="Mateo S." ${this.selectedCandidate === 'Mateo S.' ? 'selected' : ''}>Mateo S. (20m, Spanish, Medicaid - MS)</option>
              <option value="Sophia R." ${this.selectedCandidate === 'Sophia R.' ? 'selected' : ''}>Sophia R. (31m, English, Medicaid Age-Out - MS)</option>
              <option value="Elena V." ${this.selectedCandidate === 'Elena V.' ? 'selected' : ''}>Elena V. (22m, Spanish Autism Screening - TX)</option>
              <option value="Liam T." ${this.selectedCandidate === 'Liam T.' ? 'selected' : ''}>Liam T. (16m, Motor Delay - CA)</option>
            </select>
            <span class="material-symbols-outlined input-icon-right" style="pointer-events:none;">expand_more</span>
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
