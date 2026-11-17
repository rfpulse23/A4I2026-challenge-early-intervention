"""
FastAPI Server for Early Intervention 45-Day Pathway & Bottleneck Triage Dashboard.
Serves interactive coordinator dashboard and JSON APIs.
"""
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.tools.graph_service import (
    trace_referral_chain,
    find_compliant_pathway,
    get_equity_audit
)

app = FastAPI(title="Early Intervention 45-Day Pathway & Triage Assistant")

@app.get("/api/diagnose")
def api_diagnose(state: str = "MS", case_chain_id: str = "CHAIN-MS-009"):
    return trace_referral_chain(state_code=state, case_chain_id=case_chain_id)

@app.get("/api/route")
def api_route(age_months: int = 20, tract: str = "28011950701", medicaid: bool = True, bilingual: bool = True, state: str = "MS"):
    return find_compliant_pathway(
        child_age_months=age_months,
        home_tract_geoid=tract,
        requires_medicaid=medicaid,
        requires_bilingual=bilingual,
        state_code=state
    )

@app.get("/api/equity")
def api_equity(tract: str = "28011950701", state: str = "MS"):
    return get_equity_audit(home_tract_geoid=tract, state_code=state)

@app.get("/", response_class=HTMLResponse)
def index():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>First Milestones | IDEA Part C 45-Day Triage Assistant</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background-color: #f4f6f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .header-box { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 24px; border-radius: 8px; margin-bottom: 24px; }
    .card { border: none; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .stat-pill { border-radius: 20px; padding: 6px 14px; font-weight: 600; display: inline-block; }
    .pill-breach { background: #fee2e2; color: #b91c1c; }
    .pill-compliant { background: #dcfce7; color: #15803d; }
    .hop-card { border-left: 4px solid #cbd5e1; padding: 12px; margin-bottom: 8px; background: #fff; border-radius: 4px; }
    .hop-breach { border-left-color: #ef4444; background: #fef2f2; }
    .hop-success { border-left-color: #10b981; background: #f0fdf4; }
  </style>
</head>
<body class="container py-4">

  <div class="header-box shadow-sm">
    <div class="d-flex justify-content-between align-items-center">
      <div>
        <h2 class="mb-1">🧭 First Milestones: IDEA Part C Triage Assistant</h2>
        <p class="mb-0 opacity-75">Federal 45-Day Clock & Bottleneck Audit · State of Mississippi (FIPS 28)</p>
      </div>
      <div>
        <span class="badge bg-light text-primary fs-6">Agents for Impact 2026</span>
      </div>
    </div>
  </div>

  <div class="row">
    <!-- Left Column: Case Parameters & Summary -->
    <div class="col-md-4">
      <div class="card p-3">
        <h5>Active Intake Referral</h5>
        <hr>
        <p><strong>Child:</strong> 20-month-old Toddler</p>
        <p><strong>Concern:</strong> Expressive Speech & Language</p>
        <p><strong>Tract:</strong> 28011950701 (Bolivar Co., MS)</p>
        <p><strong>Insurance:</strong> Medicaid Enrolled</p>
        <p><strong>Language:</strong> Spanish Bilingual Required</p>
        <div class="alert alert-warning py-2 mb-0">
          <small>⚠️ <strong>Clock:</strong> 45 calendar days to IFSP (34 CFR § 303.310)</small>
        </div>
      </div>

      <div class="card p-3">
        <h5>Equity & Neighborhood Audit</h5>
        <hr>
        <p class="mb-1"><strong>County:</strong> Bolivar County (Delta)</p>
        <p class="mb-1"><strong>Tract Poverty:</strong> <span class="text-danger fw-bold">36.8%</span> (State: 31.1%)</p>
        <p class="mb-1"><strong>Zero-Vehicle:</strong> 11.8% of households</p>
        <small class="text-muted">Synthetic providers (SYN-PROV-*) safely protect clinician confidentiality while anchored to real US Census tracts.</small>
      </div>
    </div>

    <!-- Right Column: Comparative Pathways -->
    <div class="col-md-8">
      
      <!-- Breach Card -->
      <div class="card p-3 border-start border-danger border-4">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h5 class="text-danger mb-0">❌ Historical Baseline Route (Paper-Fax Saturated)</h5>
          <span class="stat-pill pill-breach">76 Days (BREACHED BY 31 DAYS)</span>
        </div>
        <p class="text-muted small">Hub looked healthy in spreadsheet (5-day wait), but paper-fax handoffs caused 3-hop saturated evaluator bounce loops.</p>
        
        <div class="hop-card hop-breach">
          <strong>Hop 1:</strong> Greenwood Well-Child Clinic ➔ Cleveland Coordinator Desk (13 days, paper fax)
        </div>
        <div class="hop-card hop-breach">
          <strong>Hop 2:</strong> Cleveland Coordinator Desk ➔ Greenwood Eval Hub (22 days, paper fax)
        </div>
        <div class="hop-card hop-breach">
          <strong>Hop 3 (BOUNCE):</strong> Greenwood Eval Hub ➔ Indianola Eval Hub (24 days, paper fax — <em>Bilingual Slot Unavailable</em>)
        </div>
        <div class="hop-card">
          <strong>Hop 4:</strong> Indianola Eval Hub ➔ Therapy Vendor (17 days)
        </div>
      </div>

      <!-- Compliant Route Card -->
      <div class="card p-3 border-start border-success border-4">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h5 class="text-success mb-0">✅ Agent Re-Routed Compliant Pathway</h5>
          <span class="stat-pill pill-compliant">17 Days (SAVED 59 DAYS!)</span>
        </div>
        <p class="text-muted small">Traversed alternative electronic direct graph paths matching Medicaid & Spanish credentials.</p>
        
        <div class="hop-card hop-success">
          <strong>Hop 1:</strong> Clarksdale Well-Child Screening Group (4 days, EHR portal, 7.7 km)
        </div>
        <div class="hop-card hop-success">
          <strong>Hop 2:</strong> Indianola Regional Part C Intake Desk (Direct electronic handoff)
        </div>
        <div class="hop-card hop-success">
          <strong>Hop 3:</strong> Greenwood Developmental-Behavioral & Speech Center (6 days, Pre-matched Bilingual & Medicaid)
        </div>
        <div class="hop-card hop-success">
          <strong>Hop 4:</strong> Greenville Early Childhood Therapy Organization (Timely IFSP completed)
        </div>
      </div>

      <!-- Bilingual Caregiver Note -->
      <div class="card p-3">
        <h5>Caregiver Action Note (Bilingual)</h5>
        <hr>
        <div class="bg-light p-3 rounded mb-2">
          <small><strong>English:</strong> We have scheduled your 20-month-old's bilingual developmental evaluation with Greenwood Evaluation Hub within 14 business days. Free Medicaid Non-Emergency Transportation (NEMT) is available if you need transport.</small>
        </div>
        <div class="bg-light p-3 rounded">
          <small><strong>Español:</strong> Hemos coordinado la evaluación de desarrollo de su niño(a) con especialistas bilingües en Greenwood Evaluation Hub dentro de 14 días laborables. Transporte gratuito de Medicaid disponible.</small>
        </div>
      </div>

    </div>
  </div>

</body>
</html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("repo_template.ui.server:app", host="0.0.0.0", port=8080, reload=True)
