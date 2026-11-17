"""
Google ADK Agent for Early Intervention Triage & 45-Day Pathway Optimization.
Challenge 04: Agents for Impact 2026.
Equipped with all 3 Official Tracks:
- Track 1: Today's Toddler Referral Triage (<=45d compliant bilingual routing)
- Track 2: This Quarter's Network Audit (Systemic bounce hub diagnosis & counterfactual fixes)
- Track 3: This Community Screening Season (Tract prioritization with verified downstream capacity)
Plus Advanced Extensions (GTFS Transit guardrails, Head Start/WIC sites, Real-time Slot Locks).
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure package root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from google.adk.agents import Agent
from agent.prompts.coordinator_prompt import SYSTEM_INSTRUCTION
from agent.tools.graph_service import (
    trace_referral_chain,
    find_compliant_pathway,
    get_equity_audit
)
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

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# -----------------------------------------------------------------------------
# TRACK 1 TOOLS: Today's Toddler Referral
# -----------------------------------------------------------------------------
def trace_referral_bounce_loop(case_chain_id: str = "CHAIN-MS-009", state_code: str = "MS") -> Dict[str, Any]:
    """
    [Track 1] Traces multi-hop referral chains over BigQuery referral logs to diagnose paper-fax bottlenecks
    and 3-hop bounce loops that breach the federal 45-day IDEA Part C clock.
    """
    return trace_referral_chain(state_code=state_code, case_chain_id=case_chain_id)

def find_compliant_45day_pathway(
    child_age_months: int = 20,
    home_tract_geoid: str = "28011950701",
    requires_medicaid: bool = True,
    requires_bilingual: bool = True,
    state_code: str = "MS"
) -> Dict[str, Any]:
    """
    [Track 1] Finds a verified <=45-day compliant pathway connecting an origin clinic, electronic coordinator hub,
    multidisciplinary evaluation hub, and therapy vendor matching Medicaid and bilingual requirements.
    """
    return find_compliant_pathway(
        child_age_months=child_age_months,
        home_tract_geoid=home_tract_geoid,
        requires_medicaid=requires_medicaid,
        requires_bilingual=requires_bilingual,
        state_code=state_code
    )

def run_equity_audit(home_tract_geoid: str = "28011950701", state_code: str = "MS") -> Dict[str, Any]:
    """
    [Track 1] Audits the child's home neighborhood demographics (poverty, zero-vehicle households) against state
    averages to evaluate transport barriers and ensure equitable access.
    """
    return get_equity_audit(home_tract_geoid=home_tract_geoid, state_code=state_code)


# -----------------------------------------------------------------------------
# TRACK 2 TOOLS: This Quarter's Network Audit & Bottleneck Remediation
# -----------------------------------------------------------------------------
def audit_systemic_network_bottlenecks(state_code: str = "MS") -> Dict[str, Any]:
    """
    [Track 2] Traverses all 3-to-4 hop referral chains across the state to diagnose why regional 45-day
    compliance dropped below 60%. Pinpoints deceptive bounce hubs whose low internal wait hides downstream breaches.
    """
    return diagnose_systemic_bottlenecks(state_code=state_code)

def simulate_counterfactual_network_fix(
    hub_id: str = "SYN-PROV-MS-009",
    action: str = "upgrade_to_electronic_portal",
    state_code: str = "MS"
) -> Dict[str, Any]:
    """
    [Track 2] Quantifies the systemic impact of upgrading a paper-fax intake hub or funding bilingual evaluators,
    calculating total delayed child-days saved and regional compliance percentage uplift.
    """
    return run_counterfactual_network_fix(hub_id=hub_id, action=action, state_code=state_code)


# -----------------------------------------------------------------------------
# TRACK 3 TOOLS: This Community Screening Season
# -----------------------------------------------------------------------------
def plan_community_developmental_screening_season(
    state_code: str = "MS",
    max_travel_distance_km: float = 40.0,
    top_n_tracts: int = 5
) -> Dict[str, Any]:
    """
    [Track 3] Prioritizes high-poverty, zero-vehicle Census tracts for mobile developmental screening days,
    strictly verifying downstream <=45-day evaluation capacity before screening to prevent dead-end waitlists.
    """
    return plan_community_screening_season(
        state_code=state_code,
        max_travel_distance_km=max_travel_distance_km,
        top_n_tracts=top_n_tracts
    )


# -----------------------------------------------------------------------------
# ADVANCED EXTENSION TOOLS
# -----------------------------------------------------------------------------
def check_transit_accessibility(origin_tract_geoid: str = "28011950701", target_hub_id: str = "SYN-PROV-MS-019") -> Dict[str, Any]:
    """
    [Extension 1] Determines if a zero-vehicle caregiver can reach an evaluation hub by public bus using
    BigQuery tract_transit_guardrails, or triggers automatic Medicaid Non-Emergency Transportation (NEMT).
    """
    return check_zero_vehicle_transit_feasibility(origin_tract_geoid=origin_tract_geoid, target_hub_id=target_hub_id)

def find_head_start_and_wic_screening_sites(target_county: str = "Bolivar County", require_bilingual: bool = True) -> Dict[str, Any]:
    """
    [Extension 2] Locates licensed public Head Start and WIC clinic sites for community developmental screening days.
    """
    return find_community_screening_sites(target_county=target_county, require_bilingual=require_bilingual)

def reserve_live_evaluation_slot(
    case_chain_id: str = "CHAIN-MS-009",
    provider_id: str = "SYN-PROV-MS-019",
    child_age_months: int = 20,
    coordinator_id: str = "COORD-CLARKSDALE-01"
) -> Dict[str, Any]:
    """
    [Extension 3] Atomically reserves a live evaluation slot with an ACID lock, preventing concurrent coordinators from double-booking.
    """
    return reserve_evaluation_slot(
        case_chain_id=case_chain_id,
        provider_id=provider_id,
        child_age_months=child_age_months,
        coordinator_id=coordinator_id
    )

# The root agent exposed to ADK Web and the Python SDK
root_agent = Agent(
    name="early_intervention_coordinator",
    description="IDEA Part C Early Intervention Multi-Track Coordinator & Quality Audit Agent.",
    model=MODEL,
    instruction=SYSTEM_INSTRUCTION + """

### Multi-Track Responsibilities:
1. **Track 1: Today's Toddler Referral**
   - Use `trace_referral_bounce_loop` to diagnose past failures.
   - Use `find_compliant_45day_pathway` to route children to compliant <=45-day providers.
   - Use `run_equity_audit` to evaluate neighborhood demographic context.

2. **Track 2: This Quarter's Network Audit**
   - When asked to audit regional network performance or why 45-day compliance fell below 60%, use `audit_systemic_network_bottlenecks`.
   - To simulate systemic fixes (e.g. converting a fax hub to electronic intake), use `simulate_counterfactual_network_fix`.

3. **Track 3: This Community Screening Season**
   - When planning mobile developmental screening days or coalition outreach, use `plan_community_developmental_screening_season` to identify high-risk tracts with verified downstream <=45-day capacity.
   - Pair with `find_head_start_and_wic_screening_sites` for community screening locations.
""",
    tools=[
        trace_referral_bounce_loop,
        find_compliant_45day_pathway,
        run_equity_audit,
        audit_systemic_network_bottlenecks,
        simulate_counterfactual_network_fix,
        plan_community_developmental_screening_season,
        check_transit_accessibility,
        find_head_start_and_wic_screening_sites,
        reserve_live_evaluation_slot
    ]
)

# Alias for backwards compatibility
agent = root_agent
create_coordinator_agent = lambda model_name=None: root_agent
