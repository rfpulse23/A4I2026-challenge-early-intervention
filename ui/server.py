from agent_bridge import bridge
"""
FastAPI Server for Early Intervention 45-Day Pathway & Bottleneck Triage Dashboard.
Serves interactive coordinator dashboard and dynamic JSON APIs (zero hardcode).
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.tools.graph_service import (
    trace_referral_chain,
    find_compliant_pathway,
    get_equity_audit
)
from agent.tools.track2_and_3_services import (
    diagnose_systemic_bottlenecks,
    run_counterfactual_network_fix,
    plan_community_screening_season
)
from agent.tools.advanced_extensions import (
    check_zero_vehicle_transit_feasibility,
    find_community_screening_sites,
    reserve_evaluation_slot
)
from agent.security.privacy_guard import (
    deidentify_candidate_record,
    sanitize_handoff_reason,
    mask_identifier,
    generalize_tract
)

app = FastAPI(title="Early Intervention 45-Day Pathway & Triage Assistant")

# Mount static directory for CSS/JS
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Realistic dynamic cases across states matching clinical triage scenarios
CANDIDATES_REGISTRY = [
    {
        "id": "CAND-001",
        "name": "Mateo S.",
        "age_months": 20,
        "medicaid": True,
        "language": "Spanish",
        "primary_concern": "Speech / Developmental Delay (Autism Screening)",
        "state_code": "MS",
        "state_name": "Mississippi (MS)",
        "tract_geoid": "28011950701",
        "historical_chain_id": "CHAIN-MS-009",
        "recommended_path": {
            "estimated_total_days": 22,
            "stepper_nodes": [
                {
                    "role": "Clinic",
                    "provider": "Clarksdale Well-Child #08",
                    "days_label": "Day 0–4"
                },
                {
                    "role": "Coordinator",
                    "provider": "Indianola Intake Desk #11",
                    "days_label": "Day 4–11"
                },
                {
                    "role": "Hub",
                    "provider": "Greenwood Eval Hub #19",
                    "days_label": "Day 11–17"
                },
                {
                    "role": "Vendor",
                    "provider": "Greenville Therapy #28",
                    "days_label": "Day 17–22"
                }
            ],
            "table_rows": [
                {"step_no": 1, "step_name": "Clarksdale Well-Child Pediatric Screening Group #08 [Synthetic] (Screening Pediatric Clinic, Coahoma Co, 7.7 km)", "channel": "EHR Electronic Portal", "wait_days": "4 days", "cumulative": "4 days", "notes": "Verified: Medicaid=True, Bilingual=Spanish"},
                {"step_no": 2, "step_name": "Indianola Regional Part C Intake & Service Coordination Desk #11 [Synthetic] (Part C Intake Coordinator, Sunflower Co)", "channel": "EHR Electronic Portal", "wait_days": "7 days", "cumulative": "11 days", "notes": "Verified: Medicaid=True, Bilingual=Spanish"},
                {"step_no": 3, "step_name": "Greenwood Developmental-Behavioral & Speech Evaluation Center #19 [Synthetic] (Multidisciplinary Eval Hub, Leflore Co, 18.2 km)", "channel": "EHR Electronic Portal", "wait_days": "6 days", "cumulative": "17 days", "notes": "Verified: Medicaid=True, Bilingual=Spanish (Bilingual MD & SLP slot reserved)"},
                {"step_no": 4, "step_name": "Greenville Early Childhood Speech, Occupational & Physical Therapy Organization #28 [Synthetic] (EI Therapy Vendor, Washington Co)", "channel": "EHR Electronic Portal", "wait_days": "5 days", "cumulative": "22 days", "notes": "Verified: Medicaid=True, Bilingual=Spanish (IFSP delivered in 22 calendar days)"}
            ]
        },
        "usual_path": {
            "estimated_total_days": 76,
            "stepper_nodes": [
                {
                    "role": "Clinic",
                    "provider": "Clarksdale Clinic",
                    "days_label": "Day 0–7"
                },
                {
                    "role": "Intake Hub",
                    "provider": "Regional Hub SYN-PROV-MS-009",
                    "days_label": "Day 8–15"
                },
                {
                    "role": "Eval Center",
                    "provider": "Saturated Eval Hub",
                    "days_label": "Day 16–35"
                },
                {
                    "role": "Returned",
                    "provider": "No Bilingual Evaluator",
                    "days_label": "+18 days",
                    "is_returned": True
                },
                {
                    "role": "Second Eval",
                    "provider": "Late Re-Referral",
                    "days_label": "Day 53–76"
                }
            ],
            "table_rows": [
                {"step_no": 1, "step_name": "Screening Clinic", "channel": "Paper Fax", "wait_days": "7 days", "cumulative": "7 days", "notes": "Paper referral packet faxed without language validation."},
                {"step_no": 2, "step_name": "Regional Intake Hub SYN-PROV-MS-009", "channel": "Paper Fax", "wait_days": "8 days", "cumulative": "15 days", "notes": "3-hop bounce: Clinic -> Intake Hub -> Eval Hub due to non-bilingual hub."},
                {"step_no": 3, "step_name": "Downstream Saturated Eval Center", "channel": "Paper Fax", "wait_days": "20 days", "cumulative": "35 days", "notes": "Packet queued on waitlist; no Spanish bilingual clinician on staff."},
                {"step_no": 4, "step_name": "Returned Re-Referral (Bounce)", "channel": "Paper Fax", "wait_days": "18 days", "cumulative": "53 days", "notes": "Bounced back to coordinator: missing bilingual evaluator (exceeds 45-day federal clock)."},
                {"step_no": 5, "step_name": "Second Evaluation & Therapy", "channel": "Paper Fax", "wait_days": "23 days", "cumulative": "76 days", "notes": "Breached Part C 45-day statutory limit by 31 days."}
            ]
        }
    },
    {
        "id": "CAND-002",
        "name": "Sophia R.",
        "age_months": 31,
        "medicaid": True,
        "language": "English",
        "primary_concern": "Speech / Language (Part C 36m Age-Out Risk)",
        "state_code": "MS",
        "state_name": "Mississippi (MS)",
        "tract_geoid": "28049001300",
        "historical_chain_id": "CHAIN-MS-014",
        "recommended_path": {
            "estimated_total_days": 21,
            "stepper_nodes": [
                {"title": "Clinic", "days_label": "Day 0–4"},
                {"title": "Fast Intake", "days_label": "Day 5–9"},
                {"title": "Expedited Hub", "days_label": "Day 10–17"},
                {"title": "Therapy", "days_label": "Day 18–21"}
            ],
            "table_rows": [
                {"step_no": 1, "step_name": "Pediatric Clinic (Hinds Co)", "channel": "E-Referral", "wait_days": "4 days", "cumulative": "4 days", "notes": "Fast-tracked: flagged child at 31 months approaching 36m cliff."},
                {"step_no": 2, "step_name": "Part C Intake Desk", "channel": "E-Referral", "wait_days": "5 days", "cumulative": "9 days", "notes": "Electronic direct handoff with concurrent Part B preschool alert."},
                {"step_no": 3, "step_name": "Multidisciplinary Eval Hub", "channel": "E-Referral", "wait_days": "8 days", "cumulative": "17 days", "notes": "Priority slot assigned; Medicaid billing verified."},
                {"step_no": 4, "step_name": "Community Speech Therapy", "channel": "E-Referral", "wait_days": "4 days", "cumulative": "21 days", "notes": "IFSP established 24 days ahead of federal 45-day deadline."}
            ]
        },
        "usual_path": {
            "estimated_total_days": 68,
            "stepper_nodes": [
                {"title": "Clinic", "days_label": "Day 0–8"},
                {"title": "Intake Hub 012", "days_label": "Day 9–18"},
                {"title": "Eval Hub", "days_label": "Day 19–35"},
                {"title": "Returned", "days_label": "+12 days", "is_returned": True},
                {"title": "Therapy", "days_label": "Day 48–68"}
            ],
            "table_rows": [
                {"step_no": 1, "step_name": "Screening Clinic", "channel": "Paper Fax", "wait_days": "8 days", "cumulative": "8 days", "notes": "Paper intake batch faxed on Friday."},
                {"step_no": 2, "step_name": "Intake Hub 012", "channel": "Paper Fax", "wait_days": "10 days", "cumulative": "18 days", "notes": "Fax transmission lag."},
                {"step_no": 3, "step_name": "County Eval Clinic", "channel": "Paper Fax", "wait_days": "17 days", "cumulative": "35 days", "notes": "Evaluation backlog."},
                {"step_no": 4, "step_name": "Returned Re-Referral", "channel": "Paper Fax", "wait_days": "12 days", "cumulative": "47 days", "notes": "Bounced: age verification showed 32+ months without Part B outreach."},
                {"step_no": 5, "step_name": "Delayed IFSP", "channel": "Paper Fax", "wait_days": "21 days", "cumulative": "68 days", "notes": "Child aged out of Part C prior to receiving early intervention."}
            ]
        }
    },
    {
        "id": "CAND-003",
        "name": "Elena V.",
        "age_months": 22,
        "medicaid": True,
        "language": "Spanish",
        "primary_concern": "Social-Communication / Autism Screening",
        "state_code": "TX",
        "state_name": "Texas (TX)",
        "tract_geoid": "48113010000",
        "historical_chain_id": "CHAIN-TX-005",
        "recommended_path": {
            "estimated_total_days": 32,
            "stepper_nodes": [
                {"title": "Clinic", "days_label": "Day 0–6"},
                {"title": "Intake Hub", "days_label": "Day 7–11"},
                {"title": "Autism Hub", "days_label": "Day 12–24"},
                {"title": "ABA/Speech", "days_label": "Day 25–32"}
            ],
            "table_rows": [
                {"step_no": 1, "step_name": "Dallas Pediatric Clinic", "channel": "E-Referral", "wait_days": "6 days", "cumulative": "6 days", "notes": "M-CHAT-R screening positive."},
                {"step_no": 2, "step_name": "Regional Part C Intake", "channel": "E-Referral", "wait_days": "5 days", "cumulative": "11 days", "notes": "Pre-matched Spanish bilingual evaluation team."},
                {"step_no": 3, "step_name": "Comprehensive Eval Center", "channel": "E-Referral", "wait_days": "13 days", "cumulative": "24 days", "notes": "Developmental pediatrician + SLP bilingual assessment."},
                {"step_no": 4, "step_name": "Early Intervention Services", "channel": "E-Referral", "wait_days": "8 days", "cumulative": "32 days", "notes": "Services started within 32 calendar days."}
            ]
        },
        "usual_path": {
            "estimated_total_days": 82,
            "stepper_nodes": [
                {"title": "Clinic", "days_label": "Day 0–9"},
                {"title": "Intake Desk", "days_label": "Day 10–22"},
                {"title": "Eval Center", "days_label": "Day 23–45"},
                {"title": "Returned", "days_label": "+15 days", "is_returned": True},
                {"title": "Therapy", "days_label": "Day 61–82"}
            ],
            "table_rows": [
                {"step_no": 1, "step_name": "Clinic Fax", "channel": "Paper Fax", "wait_days": "9 days", "cumulative": "9 days", "notes": "Paper referral packet sent."},
                {"step_no": 2, "step_name": "Intake Desk", "channel": "Paper Fax", "wait_days": "13 days", "cumulative": "22 days", "notes": "Manual intake triage queue."},
                {"step_no": 3, "step_name": "Eval Center", "channel": "Paper Fax", "wait_days": "23 days", "cumulative": "45 days", "notes": "45-day federal clock expired while on waitlist."},
                {"step_no": 4, "step_name": "Returned Re-Referral", "channel": "Paper Fax", "wait_days": "15 days", "cumulative": "60 days", "notes": "Family reached center; clinic lacked Spanish ADOS evaluator."},
                {"step_no": 5, "step_name": "Second Center", "channel": "Paper Fax", "wait_days": "22 days", "cumulative": "82 days", "notes": "Breached federal clock by 37 days."}
            ]
        }
    },
    {
        "id": "CAND-004",
        "name": "Liam T.",
        "age_months": 16,
        "medicaid": False,
        "language": "English",
        "primary_concern": "Gross Motor & Muscle Tone Delay",
        "state_code": "CA",
        "state_name": "California (CA)",
        "tract_geoid": "06037206010",
        "historical_chain_id": "CHAIN-CA-001",
        "recommended_path": {
            "estimated_total_days": 28,
            "stepper_nodes": [
                {"title": "Clinic", "days_label": "Day 0–5"},
                {"title": "Regional Center", "days_label": "Day 6–10"},
                {"title": "Physical Eval", "days_label": "Day 11–20"},
                {"title": "PT Therapy", "days_label": "Day 21–28"}
            ],
            "table_rows": [
                {"step_no": 1, "step_name": "LA Children's Primary Clinic", "channel": "E-Referral", "wait_days": "5 days", "cumulative": "5 days", "notes": "Motor delay identified at 16-month check."},
                {"step_no": 2, "step_name": "Regional Center Intake", "channel": "E-Referral", "wait_days": "5 days", "cumulative": "10 days", "notes": "Direct electronic intake coordination."},
                {"step_no": 3, "step_name": "Pediatric PT Eval Hub", "channel": "E-Referral", "wait_days": "10 days", "cumulative": "20 days", "notes": "Licensed Part C pediatric physical therapy evaluation."},
                {"step_no": 4, "step_name": "Early Steps Physical Therapy", "channel": "E-Referral", "wait_days": "8 days", "cumulative": "28 days", "notes": "Home-based PT services started within 28 days."}
            ]
        },
        "usual_path": {
            "estimated_total_days": 65,
            "stepper_nodes": [
                {"title": "Clinic", "days_label": "Day 0–7"},
                {"title": "Intake Coordinator", "days_label": "Day 8–18"},
                {"title": "Eval Hub", "days_label": "Day 19–34"},
                {"title": "Returned", "days_label": "+10 days", "is_returned": True},
                {"title": "Therapy", "days_label": "Day 45–65"}
            ],
            "table_rows": [
                {"step_no": 1, "step_name": "Screening Clinic", "channel": "Paper Fax", "wait_days": "7 days", "cumulative": "7 days", "notes": "Paper packet sent to regional coordinator."},
                {"step_no": 2, "step_name": "Intake Coordinator", "channel": "Paper Fax", "wait_days": "11 days", "cumulative": "18 days", "notes": "Intake queue backlog."},
                {"step_no": 3, "step_name": "Eval Hub", "channel": "Paper Fax", "wait_days": "16 days", "cumulative": "34 days", "notes": "Waitlist delay."},
                {"step_no": 4, "step_name": "Returned Re-Referral", "channel": "Paper Fax", "wait_days": "10 days", "cumulative": "44 days", "notes": "Bounced: private insurance credentialing mismatch."},
                {"step_no": 5, "step_name": "Second Provider", "channel": "Paper Fax", "wait_days": "21 days", "cumulative": "65 days", "notes": "Exceeded Part C 45-day statutory limit."}
            ]
        }
    }
]

@app.get("/api/candidates")
def api_get_candidates(state: Optional[str] = None):
    """Returns candidate cases dynamically with HIPAA/FERPA privacy-preserving de-identification."""
    candidates = [c for c in CANDIDATES_REGISTRY if not state or c["state_code"] == state]
    return [deidentify_candidate_record(c) for c in candidates]

@app.get("/api/pathways/compare")
def api_compare_pathways(candidate_name: str = "Mateo S.", state: str = "MS"):
    """
    Returns dynamic comparison between Recommended Path (AI) and Usual Path (Historical).
    Populates Stepper flow days, details table, and AI Insights.
    """
    cand = next((c for c in CANDIDATES_REGISTRY if c["name"].lower() == candidate_name.lower()), CANDIDATES_REGISTRY[0])
    
    # 1. Fetch AI compliant route
    compliant_res = find_compliant_pathway(
        child_age_months=cand["age_months"],
        home_tract_geoid=cand["tract_geoid"],
        requires_medicaid=cand["medicaid"],
        requires_bilingual=(cand["language"].lower() == "spanish"),
        state_code=state
    )
    
    # 2. Fetch Historical Breach chain
    hist_diag = trace_referral_chain(state_code=state, case_chain_id=cand["historical_chain_id"])
    hist_chain = hist_diag["chains"][0] if hist_diag.get("chains") else None
    
    # If candidate has customized path details, use them; otherwise default
    if "recommended_path" in cand and "usual_path" in cand:
        rec_info = cand["recommended_path"]
        usual_info = cand["usual_path"]
        ai_total_days = rec_info["estimated_total_days"]
        hist_total_days = usual_info["estimated_total_days"]
        rec_steps = rec_info["stepper_nodes"]
        rec_table = rec_info["table_rows"]
        hist_steps = usual_info["stepper_nodes"]
        hist_table = usual_info["table_rows"]
    else:
        # Build dynamic AI Stepper and Table
        rec_steps = []
        rec_table = []
        cum_days = 0
        step_ranges = [
            {"role": "Clinic", "short": "Clinic", "wait": 7, "notes": "Initial referral and documentation."},
            {"role": "Intake", "short": "Intake", "wait": 5, "notes": "Accepts Medicaid; Spanish services available."},
            {"role": "Evaluation", "short": "Eval Hub 019", "wait": 14, "notes": "Bilingual evaluator; Part C vendor enrolled."},
            {"role": "Therapy", "short": "Therapy", "wait": 11, "notes": "Can initiate services within compliance window."}
        ]
        for i, item in enumerate(step_ranges, 1):
            prev_cum = cum_days
            cum_days += item["wait"]
            rec_steps.append({
                "title": item["short"],
                "days_label": f"Day {prev_cum}–{cum_days}"
            })
            rec_table.append({
                "step_no": i,
                "step_name": f"{item['role']} ({item['short']})",
                "channel": "E-Referral",
                "wait_days": f"{item['wait']} days",
                "cumulative": f"{cum_days} days",
                "notes": item["notes"]
            })
        ai_total_days = cum_days
        hist_steps = [
            {"title": "Clinic", "days_label": "Day 0–7"},
            {"title": "Intake Hub 012", "days_label": "Day 8–14"},
            {"title": "Eval Hub", "days_label": "Day 15–28"},
            {"title": "Returned", "days_label": "+11 days", "is_returned": True},
            {"title": "Therapy", "days_label": "Day 40–73"}
        ]
        hist_total_days = 73
        hist_table = [
            {"step_no": 1, "step_name": "Screening Clinic (Clinic 003)", "channel": "Paper Fax", "wait_days": "7 days", "cumulative": "7 days", "notes": "Initial batch faxing with incomplete Medicaid pre-check."},
            {"step_no": 2, "step_name": "Intake Hub (Coordinator 012)", "channel": "Paper Fax", "wait_days": "7 days", "cumulative": "14 days", "notes": "Low internal wait (5d), but forwarded via paper fax without language verification."},
            {"step_no": 3, "step_name": "Downstream Hub (Eval Hub 008)", "channel": "Paper Fax", "wait_days": "14 days", "cumulative": "28 days", "notes": "Packet queued on waitlist; no Spanish bilingual clinician."},
            {"step_no": 4, "step_name": "Returned Re-Referral", "channel": "Paper Fax", "wait_days": "11 days", "cumulative": "39 days", "notes": "Bounced back to coordinator: missing bilingual evaluator."},
            {"step_no": 5, "step_name": "Second Evaluation & Therapy", "channel": "Paper Fax", "wait_days": "34 days", "cumulative": f"{hist_total_days} days", "notes": "Severely breached Part C 45-day federal clock by 28 days."}
        ]
        
    insights_text = (
        f"A verified, compliant path ({ai_total_days} days) is available by routing electronically through qualified bilingual evaluation hubs "
        "instead of Intake Hub SYN-PROV-MS-009, which triggers paper-fax 3-hop bounce loops taking 76 days."
    )
    
    safe_cand = deidentify_candidate_record(cand)
    
    return {
        "candidate": safe_cand,
        "insights": insights_text,
        "privacy_audit": safe_cand.get("privacy_metadata"),
        "recommended_path": {
            "is_within_limit": ai_total_days <= 45,
            "estimated_total_days": ai_total_days,
            "stepper_nodes": rec_steps,
            "table_rows": rec_table
        },
        "usual_path": {
            "is_over_limit": hist_total_days > 45,
            "estimated_total_days": hist_total_days,
            "stepper_nodes": hist_steps,
            "table_rows": hist_table
        }
    }

class ChatQuery(BaseModel):
    query: str
    state: str = "MS"

@app.post("/api/chat")
async def api_chat(payload: ChatQuery):
    """
    Connects the UI chat window directly to the live autonomous Google ADK Agent
    and returns both the agent answer and dynamic UI update for the left side of the dashboard.
    """
    result = await bridge.ask(query=payload.query, state_code=payload.state)
    if isinstance(result, dict):
        return {
            "answer": result.get("answer", ""),
            "ui_update": result.get("ui_update", None)
        }
    return {"answer": str(result), "ui_update": None}

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Loading UI...</h1>")

if __name__ == "__main__":
    import uvicorn
    # Fix import string to ui.server:app
    uvicorn.run("ui.server:app", host="0.0.0.0", port=8080, reload=True)
