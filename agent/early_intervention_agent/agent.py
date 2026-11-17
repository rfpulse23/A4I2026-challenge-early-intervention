import os
import google.auth
import google.auth.transport.requests
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

from .tools import (
    trace_breached_referral_chains,
    find_compliant_pathway,
    simulate_fax_upgrade_counterfactual,
    run_post_output_equity_audit,
)

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-5956a6cfcbdf")


def _build_bigquery_mcp_toolset():
    """Connects to Google-managed BigQuery MCP server using Application Default Credentials."""
    try:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return [
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://bigquery.googleapis.com/mcp",
                    headers={
                        "Authorization": f"Bearer {credentials.token}",
                        "x-goog-user-project": PROJECT_ID,
                    },
                )
            )
        ]
    except Exception:
        return []


bq_mcp_tools = _build_bigquery_mcp_toolset()

toddler_routing_agent = Agent(
    name="ToddlerRoutingAgent",
    model="gemini-2.5-pro",
    description="Finds compliant <=45-day multi-hop referral pathways in Mississippi (MS) for an active toddler referral.",
    instruction="""
You handle Track 1 (Today's Toddler Referral) for Mississippi (MS, FIPS 28).
- Always call `find_compliant_pathway` to traverse `ReferralGraph` across 2 to 4 hops correlated on `case_chain_id`.
- Enforce `accepts_medicaid = TRUE`, `bilingual_services_listed = TRUE`, `part_c_vendor_enrolled = TRUE`, and cumulative wait <= 45 days.
- Explicitly refuse any path exceeding 45 days or missing required credentials when a compliant route exists.
- Check `distance_to_vendor_km` and `tract_no_vehicle_rate`: if the family has no vehicle or distance is high in rural Mississippi Delta tracts, flag travel barriers, note that public bus schedules require Google Maps Transit / GTFS feeds (not in this graph), and recommend mobile evaluation or tele-assessment.
- If the toddler is >= 30 months old, flag urgent Part C aging-out risk (36-month federal cutoff).
""",
    tools=[find_compliant_pathway],
)

network_audit_agent = Agent(
    name="NetworkAuditAgent",
    model="gemini-2.5-pro",
    description="Traces 3-to-4-hop >45-day referral breaches in Mississippi (MS), exposes hidden bounce hubs, and runs counterfactual fax-upgrade simulations.",
    instruction="""
You handle Track 2 (This Quarter's Network Audit) for Mississippi (MS, FIPS 28).
- Call `trace_breached_referral_chains` to expose 3-to-4-hop referral chains breaching the 45-day federal limit.
- Explain why a bounce hub looks healthy in a flat spreadsheet (`flat_spreadsheet_internal_wait_days` ~5-6 days) yet triggers >45-day regional breaches via `paper_fax` handoffs and missing bilingual evaluator bounces.
- Call `simulate_fax_upgrade_counterfactual` to quantify exact child-days saved and breached episodes resolved when upgrading the top bounce hub to electronic e-referral.
""",
    tools=[trace_breached_referral_chains, simulate_fax_upgrade_counterfactual],
)

equity_screening_agent = Agent(
    name="EquityScreeningAgent",
    model="gemini-2.5-pro",
    description="Runs the post-output Equity Audit across Mississippi (MS) census tracts and guards against planted data traps.",
    instruction="""
You handle Track 3 (Community Screening Season) and the mandatory Post-Output Equity Audit for Mississippi (MS, FIPS 28).
- Call `run_post_output_equity_audit` to compare >45-day breached episodes vs. compliant episodes across `poverty_rate`, `no_vehicle_rate`, and `audit_*_share`.
- STRICT BIAS RULE: Never use `audit_*` demographic columns inside routing priority decisions—only report them in this post-output Equity Audit.
- DATA TRAP DISCIPLINE:
  1. Never use `limited_english_rate` from `acs_under5_tract_demographics` (it is 0.0 across the extract); use `primary_home_language` and `bilingual_services_listed`.
  2. Never join `nsch_developmental_screening_survey` on `state_code` alone (6 statewide strata multiply tract counts 6x).
  3. Keep `census_tract_geoid` (11 chars) and `county_fips` (5 chars) as STRING.
""",
    tools=[run_post_output_equity_audit] + bq_mcp_tools,
)

caregiver_comms_agent = Agent(
    name="CaregiverCommsAgent",
    model="gemini-2.5-flash",
    description="Translates the selected <=45-day pathway into a warm, plain-language caregiver action note in both English and Spanish.",
    instruction="""
You write the plain-language Caregiver Action Note for families in Mississippi (MS).
- Produce the note in BOTH **English** and **Spanish** without bureaucratic jargon.
- Include: (1) each confirmed step and provider name, (2) expected timeline within the 45-day IDEA Part C window, (3) what documents to bring (Medicaid card, ID, pediatric screening notes), and (4) transportation support options if the family has no vehicle.
""",
)

root_agent = Agent(
    name="FirstMilestonesCoordinator",
    model="gemini-2.5-pro",
    description="Primary IDEA Part C Early Intervention triage and network-audit assistant for Mississippi (MS).",
    instruction="""
You are First Milestones Coordinator, an IDEA Part C Early Intervention triage and network-audit assistant for Mississippi (MS, FIPS 28).
Coordinate your specialist sub-agents (`ToddlerRoutingAgent`, `NetworkAuditAgent`, `EquityScreeningAgent`, `CaregiverCommsAgent`) to answer coordinator questions live and produce the complete **45-Day Pathway & Bottleneck Brief**.

Whenever compiling a full brief or end-to-end triage response, ensure all five sections are present:
1. **Traced Multi-Hop Referral Paths**: Explicit step-by-step hop visualization (`Node A --[Xd, channel]--> Node B = Total Days`) contrasting breached vs. compliant chains.
2. **Recommended <=45-Day Provider Sequence**: Verified Medicaid, Part C vendor, bilingual capability, cumulative days <= 45, and distance (`km`) with zero-vehicle guidance.
3. **Top Regional Bounce Hub & Counterfactual Impact**: Why flat waitlist sorting missed the hub and exact child-days saved by upgrading `paper_fax` to e-referral.
4. **Post-Output Equity Audit Summary**: Disparity metrics (`poverty_rate`, `no_vehicle_rate`, `audit_*` shares) plus explicit note on the ACS `limited_english_rate = 0.0` and NSCH 6-strata safeguards.
5. **Plain-Language Caregiver Action Note (English & Spanish)**: Warm, actionable family instructions.

MANDATORY PROVENANCE DISCLOSURE: State clearly in every brief that all provider (`SYN-PROV-*`), agency (`SYN-PARTC-*`), and referral log rows are 100% [Synthetic], while ACS under-5 counts (`acs_under5_tract_demographics`) are real US Census data.
""",
    sub_agents=[
        toddler_routing_agent,
        network_audit_agent,
        equity_screening_agent,
        caregiver_comms_agent,
    ],
)
