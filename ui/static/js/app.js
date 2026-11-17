import { TopAppBar } from "./components/TopAppBar.js";
import { FilterBar } from "./components/FilterBar.js";
import { CandidateSummaryBar, AiInsightsBanner } from "./components/CandidateAndInsights.js";
import { PathwayComparison } from "./components/PathwayComparison.js";
import { GoogleCloudAssist } from "./components/GoogleCloudAssist.js";

class App {
  constructor() {
    this.currentCandidate = "Mateo S.";
    this.currentState = "MS";
    this.candidateData = {};
    this.pathwayData = {};
    this.chatMessages = [
      {
        sender: "user",
        text: "Why does Intake Hub 012 look healthy but still cause 45-day breaches?"
      },
      {
        sender: "ai",
        text: "Intake Hub 012 has a short internal wait (median 5–6 days), so it looks healthy on a spreadsheet. But 28% of similar cases are re-routed due to paper fax and eligibility mismatches, adding ~11 extra days and often pushing the total over 45 days."
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
      const res = await fetch(`/api/pathways/compare?candidate_name=${encodeURIComponent(this.currentCandidate)}&state=${this.currentState}`);
      this.pathwayData = await res.json();
      this.candidateData = this.pathwayData.candidate || {};
    } catch (e) {
      console.error("Failed to load pathway data:", e);
    }
  }

  render() {
    const root = document.getElementById("app-root");
    if (!root) return;

    const topBar = new TopAppBar("Mississippi (MS)");
    const filterBar = new FilterBar([], this.currentCandidate, this.currentState);
    const candidateSummary = new CandidateSummaryBar(this.candidateData);
    const aiInsights = new AiInsightsBanner(this.pathwayData.insights);
    const pathwayComp = new PathwayComparison(this.pathwayData);
    const assist = new GoogleCloudAssist(this.chatMessages);

    root.innerHTML = `
      <div class="app-container">
        ${topBar.render()}
        ${filterBar.render()}

        <main class="main-content">
          <!-- Left Column -->
          <div class="left-col">
            ${candidateSummary.render()}
            ${aiInsights.render()}
            ${pathwayComp.render()}
          </div>

          <!-- Right Column -->
          <div class="right-col">
            ${assist.render()}
          </div>
        </main>
      </div>
    `;
  }

  bindEvents() {
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
    const chatInput = document.getElementById("assist-input-field");
    const sendBtn = document.getElementById("btn-send-chat");
    if (chatInput && sendBtn) {
      sendBtn.addEventListener("click", () => this.handleSendChat());
      chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") this.handleSendChat();
      });
    }
  }

  async handleAnalyze() {
    const candInput = document.getElementById("input-candidate");
    if (candInput && candInput.value.trim()) {
      this.currentCandidate = candInput.value.trim();
    }
    const btn = document.getElementById("btn-analyze-pathways");
    if (btn) btn.innerHTML = `<span class="material-symbols-outlined" style="font-size:18px;">hourglass_top</span> Analyzing...`;

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
    this.chatMessages.push({ sender: "user", text: promptText });
    this.updateChatUI();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: promptText, state: this.currentState })
      });
      const data = await res.json();
      this.chatMessages.push({ sender: "ai", text: data.answer });
      this.updateChatUI();
    } catch (e) {
      this.chatMessages.push({ sender: "ai", text: "Error connecting to ADK Agent." });
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
      const assist = new GoogleCloudAssist(this.chatMessages);
      root.innerHTML = assist.render();
      // re-bind chat events
      const chatInput = document.getElementById("assist-input-field");
      const sendBtn = document.getElementById("btn-send-chat");
      if (chatInput && sendBtn) {
        sendBtn.addEventListener("click", () => this.handleSendChat());
        chatInput.addEventListener("keydown", (e) => {
          if (e.key === "Enter") this.handleSendChat();
        });
      }
      // scroll to bottom
      const history = document.getElementById("assist-chat-history");
      if (history) history.scrollTop = history.scrollHeight;
    }
  }
}

window.app = new App();
document.addEventListener("DOMContentLoaded", () => {
  window.app.init();
});
