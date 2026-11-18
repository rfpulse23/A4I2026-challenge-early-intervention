"""FastAPI & ADK HTTP Service for Cloud Run and Agent Runtime deployment.

Serves:
- Model Context Protocol (MCP) SSE Endpoint: /mcp/sse & /mcp/messages
- Interactive Web Chat UI: GET /
- Swagger / OpenAPI Docs: GET /docs
- REST Triage Brief API: POST /api/brief
- REST Natural Language Query API: POST /api/chat
- MCP Tools Discovery: GET /api/mcp/tools
"""

import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent.main_agent import coordinator_service
from agent.subagents.triage_agent import route_toddler_referral
from agent.subagents.network_audit_agent import (
    diagnose_multi_hop_breaches,
    detect_bounce_hubs,
    simulate_hub_fix,
)
from agent.subagents.equity_screening_agent import run_census_tract_equity_audit
from agent.mcp_server import mcp

app = FastAPI(
    title="First Milestones — Early Intervention Triage Agent & MCP Server API",
    description="ADK-powered Early Intervention and Network-Audit Assistant for Mississippi IDEA Part C with FastMCP SSE protocol integration.",
    version="1.1.0",
)

# Mount FastMCP SSE Server at /mcp
# This provides /mcp/sse (GET for SSE stream) and /mcp/messages (POST for JSON-RPC messages)
mcp_asgi_app = mcp.http_app(transport="sse")
app.mount("/mcp", mcp_asgi_app)


class BriefRequest(BaseModel):
    child_age_months: int = 22
    home_tract_geoid: str = "28133950100"
    primary_language: str = "Spanish"
    medicaid_enrolled: bool = True
    family_name: str = "Ramirez"
    child_name: str = "Mateo"


class ChatRequest(BaseModel):
    question: str


def process_coordinator_question(q: str) -> Dict[str, Any]:
    """Processes natural language coordinator questions and maps to specialized agent tools."""
    q_lower = q.lower()

    # Question 1: Trace multi-hop referral chains / ISO GQL / breaching 45 days
    if any(k in q_lower for k in ["trace", "multi-hop", "iso gql", "breach", "chains", "bounce"]):
        breaches = diagnose_multi_hop_breaches()
        md = "### Diagnosed Multi-Hop Referral Chains Breaching IDEA Part C (45 Days)\n\n"
        md += "**Query**: `GRAPH a4i_early_intervention.ReferralGraph MATCH (c:CareNode)-[hops:ReferralHandoff]->{2,4}(v:CareNode)`\n"
        md += "**Correlation**: `(SELECT COUNT(DISTINCT h.case_chain_id) FROM UNNEST(hops) AS h) = 1`\n\n"
        md += "| Case Chain ID | Total Hops | Total Wait Days | Fax Hops | Origin Clinic | Coordinator Hub | Notes |\n"
        md += "|---|---|---|---|---|---|---|\n"
        for b in breaches:
            md += f"| `{b['chain_id']}` | {b['total_hops']} | **{b['chain_wait_days']}d** | {b['fax_hops']} | {b['origin_clinic']} | `{b['intake_coord_id']}` | {b.get('breach_notes', 'Paper fax bounce')} |\n"
        md += "\n> **Key Finding**: Flat waitlist sorting missed these chains because Coordinator Hub 012 has an internal wait of only 5 days, yet its paper-fax transmissions trigger 3-to-4-hop re-referral chains exceeding 70 days."
        return {"response": md, "tool_used": "diagnose_multi_hop_breaches", "data": breaches}

    # Question 2: Why Coordinator Hub 012 looks healthy in spreadsheet
    if any(k in q_lower for k in ["012", "coordinator", "spreadsheet", "healthy", "bounce hub"]):
        hubs = detect_bounce_hubs()
        top = hubs[0] if hubs else {}
        md = f"### Bounce Hub Analysis: {top.get('coordinator_name')} (`{top.get('coordinator_id')}`)\n\n"
        md += f"- **Internal Wait Time in Flat Table**: **{top.get('coordinator_internal_wait_days')} days** *(looks healthy in spreadsheet)*\n"
        md += f"- **Breached Referral Chains**: Involved in **{top.get('breached_chains_involved')}** multi-hop breaches\n"
        md += f"- **Average Breached Chain Wait**: **{top.get('avg_breached_chain_wait_days')} days** *(statutory limit is 45 days)*\n"
        md += f"- **Total Excess Child Days**: **{top.get('total_excess_child_days')} days**\n\n"
        md += f"**Root Cause**: {top.get('root_cause')}\n\n"
        md += "> **Takeaway**: Sorting by `active_waitlist_count` points to downstream evaluation hubs (symptoms). Only variable-length graph traversal exposes Hub 012 as the root bottleneck."
        return {"response": md, "tool_used": "detect_bounce_hubs", "data": hubs}

    # Question 3: Routing / Compliant <=45-day path for toddler
    if any(k in q_lower for k in ["route", "pathway", "toddler", "medicaid", "spanish", "tract", "clear"]):
        routing = route_toddler_referral(
            child_age_months=22,
            home_tract_geoid="28133950100",
            primary_language="Spanish",
            medicaid_enrolled=True,
        )
        p = routing.get("recommended_pathway", {})
        md = "### Recommended Compliant <=45-Day Pathway for Today's Toddler\n\n"
        md += f"- **Child Profile**: 22-month-old toddler, Sunflower County (Tract `28133950100`), Spanish-speaking, Medicaid.\n"
        md += f"- **Total Cumulative Wait**: **{p.get('total_cumulative_wait_days')} calendar days** *(Statutory margin: +{p.get('statutory_margin_days')} days under 45-day ceiling)*\n\n"
        md += "**Traced 3-Hop Provider Sequence**:\n"
        md += f"1. **Hop 1 (Intake)**: `{p.get('hop_1', {}).get('source')}` ➔ `{p.get('hop_1', {}).get('target')}`\n"
        md += f"   - *Channel*: `{p.get('hop_1', {}).get('channel')}` | *Wait*: {p.get('hop_1', {}).get('wait_days')} days\n"
        md += f"2. **Hop 2 (Evaluation)**: `{p.get('hop_2', {}).get('source')}` ➔ `{p.get('hop_2', {}).get('target')}`\n"
        md += f"   - *Channel*: `{p.get('hop_2', {}).get('channel')}` | *Wait*: {p.get('hop_2', {}).get('wait_days')} days *(Medicaid & Spanish Bilingual Verified)*\n"
        md += f"3. **Hop 3 (Therapy Vendor)**: `{p.get('hop_3', {}).get('source')}` ➔ `{p.get('hop_3', {}).get('target')}`\n"
        md += f"   - *Channel*: `{p.get('hop_3', {}).get('channel')}` | *Wait*: {p.get('hop_3', {}).get('wait_days')} days *(Part C Enrolled Vendor)*\n"
        return {"response": md, "tool_used": "route_toddler_referral", "data": routing}

    # Question 4: Counterfactual upgrade / paper fax to e-referral
    if any(k in q_lower for k in ["upgrade", "fax", "e-referral", "counterfactual", "save", "child-days"]):
        cf = simulate_hub_fix("SYN-PROV-MS-012", "e_referral_upgrade")
        md = "### Counterfactual Policy Simulation: Upgrading Hub SYN-PROV-MS-012\n\n"
        md += f"- **Intervention**: {cf.get('intervention')}\n"
        md += f"- **Annual Delayed Child-Days Saved**: **{cf.get('total_child_days_saved_annually')} child-days**\n"
        md += f"- **Projected 45-Day Timely Compliance Gain**: **+{cf.get('projected_45d_compliance_gain_pct')}%**\n\n"
        md += f"**Policy Recommendation**: {cf.get('recommendation')}"
        return {"response": md, "tool_used": "simulate_hub_fix", "data": cf}

    # Question 5: Equity audit / demographics / neighborhoods / transit
    if any(k in q_lower for k in ["equity", "neighborhood", "demographic", "vehicle", "poverty", "county"]):
        eq = run_census_tract_equity_audit()
        md = "### Post-Output Equity Audit: Census Tract Disparities\n\n"
        md += "| Census Tract GEOID | County | Poverty Rate | Zero-Vehicle Households | Black Share | Hispanic Share | Breached Chains |\n"
        md += "|---|---|---|---|---|---|---|\n"
        for r in eq.get("equity_audit_records", []):
            md += f"| `{r['census_tract_geoid']}` | {r['county_name']} | {r['poverty_rate']*100:.1f}% | **{r['no_vehicle_rate']*100:.1f}%** | {r['audit_black_share']*100:.1f}% | {r['audit_hispanic_share']*100:.1f}% | **{r['breached_referral_count']}** |\n"
        md += f"\n**Transit Barrier Insight**: {eq.get('transit_barrier_finding')}\n\n"
        md += "**Data Trap Resolutions Applied**:\n"
        for dt in eq.get("data_traps_guardrails_applied", []):
            md += f"- *{dt['trap']}*: {dt['resolution']}\n"
        return {"response": md, "tool_used": "run_census_tract_equity_audit", "data": eq}

    # Default: Synthesize Full 45-Day Pathway & Bottleneck Brief
    brief = coordinator_service.generate_45_day_brief()
    return {
        "response": f"### Full 45-Day Pathway & Bottleneck Brief Generated\n\nProcessed query: *{q}*\n\nReview complete brief data below or select one of the specific coordinator questions.",
        "tool_used": "generate_45_day_brief",
        "data": brief,
    }


@app.get("/health")
def health_check():
    """Liveness & readiness probe."""
    return {"status": "healthy", "service": "first-milestones-ei-agent", "state": "MS", "mcp_endpoint": "/mcp/sse"}


@app.get("/api/mcp/tools")
def list_mcp_tools():
    """Returns metadata for all tools exposed over the Model Context Protocol (MCP)."""
    return {
        "mcp_server": "FirstMilestones-ReferralGraph-MCP",
        "protocol": "Model Context Protocol (MCP) 2024-11-05",
        "transport": "Server-Sent Events (SSE)",
        "endpoints": {
            "sse_connect": "/mcp/sse",
            "messages_post": "/mcp/messages",
        },
        "tools": [
            {
                "name": "trace_referral_bounce_loop",
                "description": "Traverses 2..4 hop referral chains using ISO GQL with case_chain_id correlation to diagnose multi-hop bounce loops exceeding 45 days.",
            },
            {
                "name": "find_compliant_45day_pathway",
                "description": "Discovers an optimal <=45-day compliant referral pathway for an incoming toddler matching age, Medicaid, and Spanish bilingual needs.",
            },
            {
                "name": "diagnose_bounce_hubs",
                "description": "Isolates regional coordinator hubs (e.g. SYN-PROV-MS-012) where deceptively low 5-day wait times conceal 70+ day multi-hop re-referrals.",
            },
            {
                "name": "simulate_counterfactual_network_fix",
                "description": "Simulates upgrading a paper-fax intake hub to an electronic e-referral portal, calculating delayed child-days saved.",
            },
            {
                "name": "run_equity_audit",
                "description": "Audits Census tract disparities, poverty rates, zero-vehicle transit friction, and data traps.",
            },
            {
                "name": "generate_45_day_brief",
                "description": "Compiles the full 5-part 45-Day Pathway & Bottleneck Brief for Mississippi IDEA Part C.",
            },
        ],
        "resources": [
            "referral://standards/idea-part-c",
            "bigquery://dataset/a4i_early_intervention",
        ],
    }


@app.post("/api/brief")
def generate_brief(req: BriefRequest):
    """Generates the official 45-Day Pathway & Bottleneck Brief."""
    try:
        return coordinator_service.generate_45_day_brief(
            child_age_months=req.child_age_months,
            home_tract_geoid=req.home_tract_geoid,
            primary_language=req.primary_language,
            medicaid_enrolled=req.medicaid_enrolled,
            family_name=req.family_name,
            child_name=req.child_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
def chat_with_agent(req: ChatRequest):
    """Answers natural language coordinator questions using specialized ADK tools."""
    try:
        return process_coordinator_question(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
def interactive_web_ui():
    """Serves an interactive web chat UI directly in the browser with MCP badges and docs."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>First Milestones — Early Intervention Triage Assistant & MCP Server</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f0f4f8; margin: 0; padding: 20px; color: #1a202c; }
    .container { max-width: 960px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; }
    .header { background: #1a365d; color: white; padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; }
    .header h1 { margin: 0 0 6px 0; font-size: 22px; }
    .header p { margin: 0; font-size: 14px; opacity: 0.9; }
    .badges { display: flex; gap: 8px; }
    .badge { background: #2b6cb0; color: #bee3f8; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; }
    .badge:hover { background: #2c5282; color: white; }
    .mcp-bar { background: #2d3748; color: #e2e8f0; padding: 10px 24px; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }
    .mcp-code { font-family: monospace; background: #1a202c; padding: 2px 8px; border-radius: 4px; color: #68d391; }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; padding: 16px 24px; background: #edf2f7; border-bottom: 1px solid #e2e8f0; }
    .chip { background: white; border: 1px solid #cbd5e0; border-radius: 20px; padding: 6px 14px; font-size: 13px; cursor: pointer; transition: all 0.2s; }
    .chip:hover { background: #3182ce; color: white; border-color: #3182ce; }
    .chat-box { height: 460px; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
    .msg { padding: 14px 18px; border-radius: 10px; max-width: 85%; font-size: 14px; line-height: 1.5; }
    .user { align-self: flex-end; background: #3182ce; color: white; }
    .bot { align-self: flex-start; background: #f7fafc; border: 1px solid #e2e8f0; color: #2d3748; }
    .bot table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }
    .bot th, .bot td { border: 1px solid #cbd5e0; padding: 6px 10px; text-align: left; }
    .bot th { background: #edf2f7; }
    .input-bar { display: flex; padding: 16px 24px; border-top: 1px solid #e2e8f0; background: white; gap: 12px; }
    input[type="text"] { flex: 1; padding: 12px 16px; border: 1px solid #cbd5e0; border-radius: 8px; font-size: 14px; }
    button { background: #3182ce; color: white; border: none; border-radius: 8px; padding: 0 24px; font-size: 14px; font-weight: 600; cursor: pointer; }
    button:hover { background: #2b6cb0; }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1>Early Intervention & Developmental Screening Triage (Mississippi)</h1>
        <p>Agents for Impact 2026 • ADK Multi-Agent Assistant • BigQuery Property Graphs (ISO GQL)</p>
      </div>
      <div class="badges">
        <a class="badge" href="/mcp/sse" target="_blank">MCP SSE Endpoint</a>
        <a class="badge" href="/api/mcp/tools" target="_blank">MCP Tools JSON</a>
        <a class="badge" href="/docs" target="_blank">Swagger API</a>
      </div>
    </div>
    <div class="mcp-bar">
      <span>Model Context Protocol (MCP) Server Live:</span>
      <span>SSE URL: <span class="mcp-code">/mcp/sse</span> | Post Messages: <span class="mcp-code">/mcp/messages</span></span>
    </div>
    <div class="chips">
      <div class="chip" onclick="ask(this.innerText)">Trace the 3-to-4-hop referral chains breaching the 45-day limit</div>
      <div class="chip" onclick="ask(this.innerText)">Why does Coordinator Hub 012 look healthy in a spreadsheet?</div>
      <div class="chip" onclick="ask(this.innerText)">Find a compliant <=45-day route for a Spanish Medicaid toddler</div>
      <div class="chip" onclick="ask(this.innerText)">If we upgrade Hub 012 from paper fax to e-referral, how many child-days are saved?</div>
      <div class="chip" onclick="ask(this.innerText)">Which neighborhoods bear the brunt of >45-day breaches?</div>
    </div>
    <div class="chat-box" id="chat">
      <div class="msg bot">
        <strong>First Milestones Coordinator:</strong> Hello. I am your Early Intervention triage and network-audit assistant for Mississippi IDEA Part C. All tools and graph diagnostics are also exposed over standard <strong>Model Context Protocol (MCP)</strong> at <code>/mcp/sse</code>. Click any prompt above or enter your question below.
      </div>
    </div>
    <div class="input-bar">
      <input type="text" id="userInput" placeholder="Ask a question about referral paths, bottlenecks, or routing..." onkeydown="if(event.key==='Enter') send()">
      <button onclick="send()">Send</button>
    </div>
  </div>

  <script>
    async function ask(text) {
      document.getElementById('userInput').value = text;
      send();
    }
    async function send() {
      const input = document.getElementById('userInput');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';

      const chat = document.getElementById('chat');
      chat.innerHTML += `<div class="msg user">${text}</div>`;
      chat.scrollTop = chat.scrollHeight;

      const loadingId = 'loading-' + Date.now();
      chat.innerHTML += `<div class="msg bot" id="${loadingId}"><em>Analyzing referral graph...</em></div>`;
      chat.scrollTop = chat.scrollHeight;

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({question: text})
        });
        const data = await res.json();
        const html = marked.parse(data.response || JSON.stringify(data));
        document.getElementById(loadingId).innerHTML = html;
      } catch (err) {
        document.getElementById(loadingId).innerText = "Error: " + err;
      }
      chat.scrollTop = chat.scrollHeight;
    }
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("agent.server:app", host="0.0.0.0", port=port, reload=False)
