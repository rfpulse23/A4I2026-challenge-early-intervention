export class TopAppBar {
  constructor(stateName = "Mississippi (MS)") {
    this.stateName = stateName;
  }

  render() {
    return `
      <header class="top-app-bar">
        <div class="top-bar-left">
          <div class="google-cloud-logo">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" fill="#4285F4"/>
            </svg>
            <span>Google Cloud</span>
          </div>
          <div class="app-divider"></div>
          <span class="app-title-header">Early Intervention Triage & Network-Audit Assistant</span>
          <span class="app-subtitle-header">(IDEA Part C · <span id="header-state-name">${this.stateName}</span>)</span>
        </div>
        <div class="top-bar-right">
          <button class="icon-btn" title="Notifications">
            <span class="material-symbols-outlined">notifications</span>
          </button>
          <button class="icon-btn" title="Help & Standards">
            <span class="material-symbols-outlined">help_outline</span>
          </button>
          <div class="user-badge" title="Role: Regional Intake Coordinator">
            <div class="avatar-circle">IC</div>
            <span>Intake Coordinator</span>
            <span class="material-symbols-outlined" style="font-size: 16px; margin-left: 2px;">arrow_drop_down</span>
          </div>
        </div>
      </header>
    `;
  }
}
