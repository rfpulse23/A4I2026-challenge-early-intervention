"""
Google ADK Specialized Sub-Agents and Multi-Agent Orchestration Layer.
Challenge 04: Agents for Impact 2026.

This module defines specialized sub-agents for each track:
1. toddler_referral_subagent (Track 1): Case routing, ISO GQL variable-length graph traversal, ACID slot locks.
2. network_audit_subagent (Track 2): Systemic bottleneck diagnosis, counterfactual simulations, aging-out triage.
3. community_screening_subagent (Track 3): High-poverty tract prioritization with verified downstream capacity.
4. transit_equity_subagent: Rural zero-vehicle transit guardrails, GTFS analysis, and Medicaid NEMT dispatch.
5. multi_track_orchestrator: Supervisor agent coordinating all sub-agents.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure package root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from google.adk.agents import Agent

from agent.tools.graph_service import (
    trace_referral_chain,
    find_compliant_pathway,
    get_equity_audit
)
from agent.tools.gql_traversal_service import traverse_referral_property_graph
from agent.tools.advanced_extensions import (
    check_zero_vehicle_transit_feasibility,
    find_community_screening_sites,
    reserve_evaluation_slot
)
from agent.tools.track2_and_3_services import (
    diagnose_systemic_bottlenecks,
    run_counterfactual_network_fix,
    plan_community_screening_season
)
from agent.tools.bonus_services import (
    simulate_counterfactual_bottlenecks,
    triage_aging_out_risk,
    prioritize_byod_community_screening
)

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# =============================================================================
# TRACK 1 SUB-AGENT: Toddler Referral Triage Specialist
# =============================================================================
def track1_traverse_property_graph(
    origin_clinic: str = "Clarksdale",
    requires_medicaid: bool = True,
    requires_bilingual: bool = True,
    max_days: int = 45,
    state_code: str = "MS"
) -> Dict[str, Any]:
    """Traverses BigQuery property graph using ISO GQL to find <=45-day compliant pathways."""
    return traverse_referral_property_graph(
        origin_clinic_name=origin_clinic,
        requires_medicaid=requires_medicaid,
        requires_bilingual=requires_bilingual,
        max_days=max_days,
        state_code=state_code
    )

def track1_find_compliant_pathway(
    child_age_months: int = 20,
    county_or_tract: str = "28011950701",
    requires_medicaid: bool = True,
    language: str = "Spanish",
    state_code: str = "MS"
) -> Dict[str, Any]:
    """Finds optimal 4-hop pathway avoiding historical paper-fax bounce loops."""
    return find_compliant_pathway(
        child_age_months=child_age_months,
        county_or_tract=county_or_tract,
        requires_medicaid=requires_medicaid,
        language=language,
        state_code=state_code
    )

def track1_reserve_slot_lock(
    case_chain_id: str = "CHAIN-MS-009",
    provider_id: str = "SYN-PROV-MS-019",
    child_age_months: int = 20,
    coordinator_id: str = "COORD-CLARKSDALE-01"
) -> Dict[str, Any]:
    """Atomically locks an evaluation slot with an ACID token to prevent concurrent double-booking."""
    return reserve_evaluation_slot(
        case_chain_id=case_chain_id,
        provider_id=provider_id,
        child_age_months=child_age_months,
        coordinator_id=coordinator_id
    )

toddler_referral_subagent = Agent(
    name="toddler_referral_subagent",
    description="Specialized sub-agent for Track 1: Toddler referral routing, ISO GQL property graph traversal, and ACID slot locking under federal 45-day SLA.",
    model=MODEL,
    instruction="""
You are the Track 1 Toddler Referral Specialist for IDEA Part C Early Intervention.
Your mandate:
1. Route toddlers (e.g. 20-month-old Mateo S. from Bolivar County) under the 45-day statutory clock (34 CFR § 303.310).
2. Use ISO GQL variable-length property graph traversal to find active compliant routes.
3. Reserve scarce bilingual evaluation slots atomically with ACID locks to prevent double-booking.
4. Always provide empathetic caregiver action plans in both English and Spanish.
""",
    tools=[
        track1_traverse_property_graph,
        track1_find_compliant_pathway,
        track1_reserve_slot_lock
    ]
)

# =============================================================================
# TRACK 2 SUB-AGENT: Network Quality & Bottleneck Auditor
# =============================================================================
def track2_diagnose_systemic_bottlenecks(state_code: str = "MS") -> Dict[str, Any]:
    """Identifies upstream bounce hubs causing 3-to-4 hop delays and exposes the 'Spreadsheet Trap'."""
    return diagnose_systemic_bottlenecks(state_code=state_code)

def track2_simulate_counterfactual_fix(
    hub_provider_id: str = "SYN-PROV-MS-009",
    policy_action: str = "upgrade_to_electronic_portal",
    state_code: str = "MS"
) -> Dict[str, Any]:
    """Simulates child-days saved and compliance recovery if a bottleneck hub upgrades from paper fax to an electronic portal."""
    return run_counterfactual_network_fix(
        hub_provider_id=hub_provider_id,
        policy_action=policy_action,
        state_code=state_code
    )

def track2_statewide_counterfactual_simulation(state_code: str = "MS") -> Dict[str, Any]:
    """Simulates statewide replacement of paper fax with electronic referral portals (Official Challenge Query 4)."""
    return simulate_counterfactual_bottlenecks(state_code=state_code)

def track2_aging_out_triage(child_age_months: int = 32) -> Dict[str, Any]:
    """Triages toddlers nearing 36 months under Part C age-out termination and triggers mandatory LEA Part B transition (Query 5)."""
    return triage_aging_out_risk(child_age_months=child_age_months)

network_audit_subagent = Agent(
    name="network_audit_subagent",
    description="Specialized sub-agent for Track 2: Systemic bottleneck diagnosis, deceptive intake hub audits ('Spreadsheet Trap'), counterfactual simulations (Query 4), and 32-month aging-out triage (Query 5).",
    model=MODEL,
    instruction="""
You are the Track 2 Network Quality Auditor for regional IDEA Part C quality leads.
Your mandate:
1. Diagnose why 45-day timely IFSP compliance dropped below 60%.
2. Unmask deceptive intake hubs (e.g. SYN-PROV-MS-009) whose internal queue is only 5 days, but whose paper faxes cause 537 downstream delay days.
3. Run counterfactual simulations showing that switching to electronic portals recovers breached episodes and saves over 1,000 child-days.
4. Protect children turning 3 from aging out without services (34 CFR § 303.209).
""",
    tools=[
        track2_diagnose_systemic_bottlenecks,
        track2_simulate_counterfactual_fix,
        track2_statewide_counterfactual_simulation,
        track2_aging_out_triage
    ]
)

# =============================================================================
# TRACK 3 SUB-AGENT: Community Screening Season Planner
# =============================================================================
def track3_plan_screening_season(
    state_code: str = "MS",
    max_travel_distance_km: float = 40.0,
    top_n_tracts: int = 5
) -> Dict[str, Any]:
    """Ranks high-poverty, zero-vehicle census tracts, verifying downstream <=45d evaluation capacity to avoid dead-end waitlists."""
    return plan_community_screening_season(
        state_code=state_code,
        max_travel_distance_km=max_travel_distance_km,
        top_n_tracts=top_n_tracts
    )

def track3_locate_byod_partner_sites(target_county: str = "Bolivar County", require_bilingual: bool = True) -> Dict[str, Any]:
    """Finds licensed public Head Start and WIC centers to co-locate mobile screening days (Official Challenge Query 6)."""
    return find_community_screening_sites(target_county=target_county, require_bilingual=require_bilingual)

def track3_prioritize_byod_deployment(state_code: str = "MS", limit: int = 5) -> Dict[str, Any]:
    """Prioritizes BYOD community screening deployment across underserved counties."""
    return prioritize_byod_community_screening(state_code=state_code, limit=limit)

community_screening_subagent = Agent(
    name="community_screening_subagent",
    description="Specialized sub-agent for Track 3: Community screening season planner prioritizing under-5 high-poverty, zero-vehicle tracts with strictly verified downstream <=45-day capacity, plus Head Start / WIC co-location (Query 6).",
    model=MODEL,
    instruction="""
You are the Track 3 Community Screening Season Planner for early childhood coalitions.
Your mandate:
1. Prioritize mobile screening days for high-poverty, high zero-vehicle neighborhoods.
2. ENFORCE THE CAPACITY GUARDRAIL: Never deploy a screening van unless downstream evaluation capacity <=45 days is verified. (Screening without capacity creates unethical dead-end waitlists).
3. Partner with licensed Head Start and county WIC clinics for co-located screening days.
""",
    tools=[
        track3_plan_screening_season,
        track3_locate_byod_partner_sites,
        track3_prioritize_byod_deployment
    ]
)

# =============================================================================
# TRANSIT & EQUITY SUB-AGENT: Rural Accessibility Guardrails
# =============================================================================
def transit_check_accessibility(
    tract_geoid: str = "28011950701",
    evaluation_hub_provider_id: str = "SYN-PROV-MS-019"
) -> Dict[str, Any]:
    """Calculates zero-vehicle burden, travel distance, and bus transit feasibility, triggering automated Medicaid NEMT dispatch."""
    return check_zero_vehicle_transit_feasibility(
        tract_geoid=tract_geoid,
        evaluation_hub_provider_id=evaluation_hub_provider_id
    )

def transit_run_equity_audit(state_code: str = "MS") -> Dict[str, Any]:
    """Runs a regional equity audit comparing rural vs urban timely IFSP access disparities."""
    return get_equity_audit(state_code=state_code)

transit_equity_subagent = Agent(
    name="transit_equity_subagent",
    description="Specialized sub-agent for Transit & Equity: Analyzes rural transit accessibility, zero-vehicle burdens, and automatically dispatches Medicaid Non-Emergency Transportation (NEMT).",
    model=MODEL,
    instruction="""
You are the Transit & Equity Specialist for rural families accessing Part C early intervention.
Your mandate:
1. When asked if a zero-vehicle caregiver can reach a hub by public bus, evaluate census tract demographics and transit routes.
2. In rural areas lacking public transit (e.g. Bolivar County to Greenwood, 159.2 km), report Public Transit = FALSE.
3. Automatically trigger Medicaid Non-Emergency Medical Transportation (NEMT) dispatch directives.
4. Draft empathetic family notes explaining that free Medicaid rides will be coordinated.
""",
    tools=[
        transit_check_accessibility,
        transit_run_equity_audit
    ]
)

# =============================================================================
# SUPERVISOR ORCHESTRATOR AGENT: Multi-Track Coordinator
# =============================================================================
multi_track_orchestrator = Agent(
    name="multi_track_orchestrator",
    description="Supervisor Orchestrator Agent delegating across Track 1, Track 2, Track 3, and Transit Equity sub-agents.",
    model=MODEL,
    instruction="""
You are the Supervisor Orchestrator Agent for Challenge 04: Agents for Impact 2026.
You oversee and coordinate 4 specialized sub-agents:
1. toddler_referral_subagent (Track 1)
2. network_audit_subagent (Track 2)
3. community_screening_subagent (Track 3)
4. transit_equity_subagent (Transit & Equity)

Operational Guidelines:
- If the user asks about an individual toddler, ISO GQL graph traversal, or ACID slot reservations: delegate to toddler_referral_subagent.
- If the user asks about regional compliance, deceptive hubs, paper-fax remediation, or aging-out risk: delegate to network_audit_subagent.
- If the user asks about mobile screening season, tract prioritization, or Head Start/WIC co-location: delegate to community_screening_subagent.
- If the user asks about zero-vehicle families, public bus accessibility, or NEMT rides: delegate to transit_equity_subagent.
- Never stall for missing parameters; apply benchmark defaults and generate compassionate, plain-language caregiver action notes in both English and Spanish.
""",
    tools=[
        # Direct tool exposure to ensure 100% interoperability across all runners
        track1_traverse_property_graph,
        track1_find_compliant_pathway,
        track1_reserve_slot_lock,
        track2_diagnose_systemic_bottlenecks,
        track2_simulate_counterfactual_fix,
        track2_statewide_counterfactual_simulation,
        track2_aging_out_triage,
        track3_plan_screening_season,
        track3_locate_byod_partner_sites,
        track3_prioritize_byod_deployment,
        transit_check_accessibility,
        transit_run_equity_audit
    ]
)
