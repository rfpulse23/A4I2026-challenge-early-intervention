import { TopAppBar } from "./components/TopAppBar.js";
import { FilterBar } from "./components/FilterBar.js";
import { CandidateSummaryBar, AiInsightsBanner } from "./components/CandidateAndInsights.js";
import { PathwayComparison } from "./components/PathwayComparison.js";
import { GoogleCloudAssist } from "./components/GoogleCloudAssist.js";
import { NetworkAuditPanel, ScreeningSeasonPanel } from "./components/TrackPanels.js";

class App {
  constructor() {
    this.currentTrack = "new_case"; // "new_case" (Track 1), "network_audit" (Track 2), "screening_season" (Track 3)
    this.currentCandidate = "Mateo S.";
    this.currentState = "MS";
    this.candidateData = {};
    this.pathwayData = {};
    this.auditData = {};
    this.screeningData = {};
    this.isLoadingChat = false;
    this.chatMessages = [
      {
        sender: "user",
        text: "How does the assistant coordinate all 3 IDEA Part C tracks under the federal 45-day clock?"
      },
      {
        sender: "ai",
        text: "Welcome! Our assistant coordinates across all 3 tracks:\n• Track 1: Routes 20-month toddlers like Mateo S. to bilingual Medicaid evaluators under 45 days.\n• Track 2: Audits regional networks, exposing 3-hop paper-fax bounce hubs.\n• Track 3: Prioritizes high-poverty zero-vehicle tracts for community screening only when downstream <=45-day capacity is strictly verified."
      }
    ];
  }

  async init() {
    await this.fetchData();
    this.render();
    this.bindEvents();
  }

  async fetchData() {
    try {
      if (this.currentTrack === "new_case") {
        const res = await fetch(`/api/pathways/compare?candidate_name=${encodeURIComponent(this.currentCandidate)}&state=${this.currentState}`);
        this.pathwayData = await res.json();
        this.candidateData = this.pathwayData.candidate || {};
      } else if (this.currentTrack === "network_audit") {
        const res = await fetch(`/api/tracks/network-audit?state=${this.currentState}`);
        this.auditData = await res.json();
      } else if (this.currentTrack === "screening_season") {
        const res = await fetch(`/api/tracks/screening-season?state=${this.currentState}`);
        this.screeningData = await res.json();
      }
    } catch (e) {
      console.error("Failed to load track data:", e);
    }
  }

  render() {
    const root = document.getElementById("app-root");
    if (!root) return;

    const topBar = new TopAppBar(this.getStateName(this.currentState));
    const filterBar = new FilterBar([], this.currentCandidate, this.currentState, this.currentTrack);
    const assist = new GoogleCloudAssist(this.chatMessages, this.currentTrack);

    let mainLeftContent = "";

    if (this.currentTrack === "new_case") {
      const candidateSummary = new CandidateSummaryBar(this.candidateData);
      const aiInsights = new AiInsightsBanner(this.pathwayData.insights);
      const pathwayComp = new PathwayComparison(this.pathwayData);
      mainLeftContent = `
        ${candidateSummary.render()}
        ${aiInsights.render()}
        ${pathwayComp.render()}
      `;
    } else if (this.currentTrack === "network_audit") {
      const auditPanel = new NetworkAuditPanel(this.auditData);
      mainLeftContent = auditPanel.render();
    } else if (this.currentTrack === "screening_season") {
      const screeningPanel = new ScreeningSeasonPanel(this.screeningData);
      mainLeftContent = screeningPanel.render();
    }

    root.innerHTML = `
      <div class="app-container">
        ${topBar.render()}
        ${filterBar.render()}

        <main class="main-content">
          <!-- Left Column (Active Track View) -->
          <div class="left-col">
            ${mainLeftContent}
          </div>

          <!-- Right Column (Conversational ADK Co-Pilot) -->
          <div class="right-col">
            ${assist.render()}
          </div>
        </main>
      </div>
    `;
  }

  getStateName(code) {
    const map = {
      MS: "Mississippi (MS)",
      AL: "Alabama (AL)",
      GA: "Georgia (GA)",
      TX: "Texas (TX)",
      CA: "California (CA)",
      NY: "New York (NY)"
    };
    return map[code] || `${code}`;
  }

  bindEvents() {
    // Task Mode Track Selector Change
    const taskModeSelect = document.getElementById("select-task-mode");
    if (taskModeSelect) {
      taskModeSelect.value = this.currentTrack;
      taskModeSelect.addEventListener("change", async (e) => {
        this.currentTrack = e.target.value;
        await this.handleTrackSwitch();
      });
    }

    // Analyze button
    const btnAnalyze = document.getElementById("btn-analyze-pathways");
    if (btnAnalyze) {
      btnAnalyze.addEventListener("click", () => this.handleAnalyze());
    }

    // Input Candidate enter key
    const candInput = document.getElementById("input-candidate");
    if (candInput) {
      candInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") this.handleAnalyze();
      });
    }

    // Clear candidate input
    const clearBtn = document.getElementById("clear-candidate-btn");
    if (clearBtn && candInput) {
      clearBtn.addEventListener("click", () => {
        candInput.value = "";
        candInput.focus();
      });
    }

    // Region change
    const regSelect = document.getElementById("select-region");
    if (regSelect) {
      regSelect.addEventListener("change", (e) => {
        this.currentState = e.target.value;
        const text = e.target.options[e.target.selectedIndex].text;
        const hdr = document.getElementById("header-state-name");
        if (hdr) hdr.textContent = text;
        this.handleAnalyze();
      });
    }

    // Chat input
    this.bindChatEvents();
  }

  bindChatEvents() {
    const chatInput = document.getElementById("assist-input-field");
    const sendBtn = document.getElementById("btn-send-chat");
    if (chatInput && sendBtn) {
      sendBtn.onclick = () => this.handleSendChat();
      chatInput.onkeydown = (e) => {
        if (e.key === "Enter") this.handleSendChat();
      };
    }
  }

  async handleTrackSwitch() {
    await this.fetchData();
    this.render();
    this.bindEvents();
  }

  async handleAnalyze() {
    const candInput = document.getElementById("input-candidate");
    if (candInput && candInput.value.trim()) {
      this.currentCandidate = candInput.value.trim();
    }
    const btn = document.getElementById("btn-analyze-pathways");
    if (btn) btn.innerHTML = `<span class="material-symbols-outlined" style="font-size:18px;">hourglass_top</span> Updating...`;

    await this.fetchData();
    this.render();
    this.bindEvents();
  }

  toggleAccordion(type) {
    const body = document.getElementById(`body-${type}`);
    const arrow = document.getElementById(`arrow-${type}`);
    const header = document.getElementById(`header-${type}`);
    if (!body || !arrow || !header) return;

    if (body.style.display === "none") {
      body.style.display = "block";
      arrow.textContent = "expand_more";
      header.classList.add("open");
    } else {
      body.style.display = "none";
      arrow.textContent = "chevron_right";
      header.classList.remove("open");
    }
  }

  async askPrompt(promptText) {
    if (!promptText || !promptText.trim()) return;
    if (this.isLoadingChat) return;

    this.isLoadingChat = true;
    this.chatMessages.push({ sender: "user", text: promptText.trim() });
    
    // Add temporary loading indicator
    this.chatMessages.push({ sender: "ai", text: "Analyzing across BigQuery & Property Graph..." });
    this.updateChatUI();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: promptText.trim(), state: this.currentState })
      });
      const data = await res.json();
      
      // Replace the loading message with the real answer
      this.chatMessages.pop();
      this.chatMessages.push({ sender: "ai", text: data.answer || "No response received." });
    } catch (e) {
      console.error("Chat error:", e);
      this.chatMessages.pop();
      this.chatMessages.push({ sender: "ai", text: "Error: Unable to connect to the backend agent server." });
    } finally {
      this.isLoadingChat = false;
      this.updateChatUI();
    }
  }

  async handleSendChat() {
    const input = document.getElementById("assist-input-field");
    if (!input || !input.value.trim()) return;
    const text = input.value.trim();
    input.value = "";
    await this.askPrompt(text);
  }

  updateChatUI() {
    const root = document.querySelector(".right-col");
    if (root) {
      const assist = new GoogleCloudAssist(this.chatMessages, this.currentTrack);
      root.innerHTML = assist.render();
      this.bindChatEvents();
      
      const history = document.getElementById("assist-chat-history");
      if (history) {
        history.scrollTop = history.scrollHeight;
      }
    }
  }
}

window.app = new App();
document.addEventListener("DOMContentLoaded", () => {
  window.app.init();
});
