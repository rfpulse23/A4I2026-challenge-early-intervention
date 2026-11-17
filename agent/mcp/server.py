"""
Model Context Protocol (MCP) Server for Early Intervention 45-Day Referral Graph.
Built with FastMCP to access and query Google Cloud BigQuery dataset:
`qwiklabs-gcp-04-5956a6cfcbdf.a4i_early_intervention`

Exposed BigQuery Tables:
- pediatric_and_ei_provider_directory (CareNode vertices)
- deidentified_part_c_referral_logs (ReferralHandoff edges)
- acs_under5_tract_demographics (Census under-5 demographic baselines)
- idea_part_c_agency_performance (Agency 45-day statutory compliance)
- nsch_developmental_screening_survey (HRSA statewide screening strata)
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add repo root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastmcp import FastMCP
from agent.tools.graph_service import (
    trace_referral_chain,
    find_compliant_pathway,
    get_equity_audit
)
from agent.mcp.bigquery_client import (
    PROJECT_ID,
    DATASET_ID,
    query_care_nodes,
    query_referral_logs,
    query_tract_demographics
)

# Initialize FastMCP Server
mcp = FastMCP(
    name="FirstMilestones-BigQuery-ReferralGraph-MCP",
    instructions=f"MCP Server connected to BigQuery dataset {PROJECT_ID}.{DATASET_ID} for Early Intervention Part C 45-day clock routing, bottleneck detection, and equity auditing."
)

@mcp.tool(
    name="bigquery_inspect_dataset_schema",
    description=f"Inspects the BigQuery tables and schema in dataset {PROJECT_ID}.{DATASET_ID}."
)
def mcp_inspect_dataset_schema() -> Dict[str, Any]:
    """Returns the registered BigQuery tables and their architectural roles."""
    return {
        "project_id": PROJECT_ID,
        "dataset_id": DATASET_ID,
        "tables": {
            "pediatric_and_ei_provider_directory": {
                "type": "CareNode Vertices",
                "description": "30 nodes per state (Clinics, Coordinators, Multidisciplinary Eval Hubs, Therapy Vendors)"
            },
            "deidentified_part_c_referral_logs": {
                "type": "ReferralHandoff Edges",
                "description": "149 edges across 44 multi-hop referral chains per state, tracking transmission channels and wait times"
            },
            "acs_under5_tract_demographics": {
                "type": "Relational Demographics",
                "description": "Real US Census tracts reporting under-5 poverty rates and zero-vehicle households"
            },
            "idea_part_c_agency_performance": {
                "type": "Agency Metrics",
                "description": "State IDEA Part C regional lead agency 45-day timely IFSP compliance rates"
            },
            "nsch_developmental_screening_survey": {
                "type": "Statewide Survey",
                "description": "HRSA National Survey of Children's Health developmental screening baselines"
            }
        },
        "property_graph": f"{DATASET_ID}.ReferralGraph"
    }

@mcp.tool(
    name="trace_referral_bounce_loop",
    description="Executes multi-hop referral graph traversal over BigQuery referral logs to diagnose paper-fax bottlenecks and 3-hop bounce loops exceeding the 45-day federal IDEA Part C clock."
)
def mcp_trace_referral_bounce_loop(state_code: str = "MS", case_chain_id: Optional[str] = "CHAIN-MS-009") -> Dict[str, Any]:
    """
    Traces multi-hop referral chains and returns hop-by-hop breakdown, transmission channels,
    and cumulative wait days against the 45-day federal ceiling.
    """
    return trace_referral_chain(state_code=state_code, case_chain_id=case_chain_id)

@mcp.tool(
    name="find_compliant_45day_pathway",
    description="Queries BigQuery provider directory and graph edges to find an optimal <=45-day compliant referral pathway for an incoming toddler matching age, Medicaid, and Spanish bilingual requirements."
)
def mcp_find_compliant_45day_pathway(
    child_age_months: int = 20,
    home_tract_geoid: str = "28011950701",
    requires_medicaid: bool = True,
    requires_bilingual: bool = True,
    max_days: int = 45,
    state_code: str = "MS"
) -> Dict[str, Any]:
    """
    Finds a compliant provider sequence: Clinic -> Electronic Coordinator Hub -> Bilingual Eval Hub -> Therapy Vendor.
    """
    return find_compliant_pathway(
        child_age_months=child_age_months,
        home_tract_geoid=home_tract_geoid,
        requires_medicaid=requires_medicaid,
        requires_bilingual=requires_bilingual,
        max_days=max_days,
        state_code=state_code
    )

@mcp.tool(
    name="run_equity_audit",
    description="Queries BigQuery acs_under5_tract_demographics to audit the child's home neighborhood demographics (poverty rate, zero-vehicle rate, racial/ethnic shares) against state averages."
)
def mcp_run_equity_audit(home_tract_geoid: str = "28011950701", state_code: str = "MS") -> Dict[str, Any]:
    """
    Runs post-output equity audit joining tract GEOID to Census under-5 ACS demographics.
    """
    return get_equity_audit(home_tract_geoid=home_tract_geoid, state_code=state_code)

@mcp.resource("bigquery://dataset/a4i_early_intervention")
def get_bigquery_dataset_resource() -> str:
    """Returns BigQuery connection metadata and URI."""
    return f"""
    BigQuery Dataset: {PROJECT_ID}.{DATASET_ID}
    Console URL: https://console.cloud.google.com/bigquery?ws=!1m4!1m3!3m2!1s{PROJECT_ID}!2s{DATASET_ID}
    Reservation: a4i-graph (Enterprise 0-baseline autoscale)
    Property Graph: CREATE OR REPLACE PROPERTY GRAPH {DATASET_ID}.ReferralGraph
    """

@mcp.resource("referral://standards/idea-part-c")
def get_idea_part_c_standards() -> str:
    """Returns statutory IDEA Part C 45-day timeline and equity compliance rules."""
    return """
    INDIVIDUALS WITH DISABILITIES EDUCATION ACT (IDEA) - PART C (34 CFR § 303.310)
    1. 45-Day Statutory Clock: From referral date, lead agency has 45 calendar days to complete
       multidisciplinary evaluation and convene the initial IFSP meeting.
    2. Language & Cultural Equity: Evaluations must be conducted in the family's native language.
    3. Medicaid Rights: Part C evaluations and service coordination are free to families.
    """

if __name__ == "__main__":
    mcp.run()

# -----------------------------------------------------------------------------
# Advanced Extension Tools
# -----------------------------------------------------------------------------
from agent.tools.advanced_extensions import (
    check_zero_vehicle_transit_feasibility,
    find_community_screening_sites,
    reserve_evaluation_slot
)

@mcp.tool(
    name="check_transit_accessibility",
    description="Determines if a zero-vehicle caregiver can reach an evaluation hub by public bus using transit GTFS or if Medicaid Non-Emergency Transportation (NEMT) is required."
)
def mcp_check_transit_accessibility(origin_tract_geoid: str = "28011950701", target_hub_id: str = "SYN-PROV-MS-019") -> Dict[str, Any]:
    return check_zero_vehicle_transit_feasibility(origin_tract_geoid=origin_tract_geoid, target_hub_id=target_hub_id)

@mcp.tool(
    name="find_head_start_and_wic_screening_sites",
    description="Locates licensed public Head Start and WIC sites for community screening days where high-poverty, zero-vehicle families gather."
)
def mcp_find_screening_sites(target_county: str = "Bolivar County", require_bilingual: bool = True) -> Dict[str, Any]:
    return find_community_screening_sites(target_county=target_county, require_bilingual=require_bilingual)

@mcp.tool(
    name="reserve_evaluation_slot",
    description="Atomically reserves a live multidisciplinary evaluation slot to prevent concurrent coordinators from double-booking capacity."
)
def mcp_reserve_slot(case_chain_id: str = "CHAIN-MS-009", provider_id: str = "SYN-PROV-MS-019", child_age_months: int = 20) -> Dict[str, Any]:
    return reserve_evaluation_slot(case_chain_id=case_chain_id, provider_id=provider_id, child_age_months=child_age_months)

# -----------------------------------------------------------------------------
# Track 2 & Track 3 Tools
# -----------------------------------------------------------------------------
from agent.tools.track2_and_3_services import (
    diagnose_systemic_bottlenecks,
    run_counterfactual_network_fix,
    plan_community_screening_season
)

@mcp.tool(
    name="audit_systemic_network_bottlenecks",
    description="[Track 2] Traverses all 3-to-4 hop referral chains to diagnose why regional compliance dropped below 60% and pinpoints deceptive bounce hubs."
)
def mcp_diagnose_bottlenecks(state_code: str = "MS") -> Dict[str, Any]:
    return diagnose_systemic_bottlenecks(state_code=state_code)

@mcp.tool(
    name="simulate_counterfactual_network_fix",
    description="[Track 2] Simulates upgrading a paper-fax intake hub to an electronic portal, calculating total delayed child-days saved and compliance uplift."
)
def mcp_counterfactual_fix(hub_id: str = "SYN-PROV-MS-009", action: str = "upgrade_to_electronic_portal", state_code: str = "MS") -> Dict[str, Any]:
    return run_counterfactual_network_fix(hub_id=hub_id, action=action, state_code=state_code)

@mcp.tool(
    name="plan_community_developmental_screening_season",
    description="[Track 3] Prioritizes high-poverty, zero-vehicle Census tracts for mobile screening days, verifying downstream <=45-day evaluation capacity."
)
def mcp_plan_screening(state_code: str = "MS", max_travel_distance_km: float = 40.0, top_n_tracts: int = 5) -> Dict[str, Any]:
    return plan_community_screening_season(state_code=state_code, max_travel_distance_km=max_travel_distance_km, top_n_tracts=top_n_tracts)
