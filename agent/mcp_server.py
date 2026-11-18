"""Model Context Protocol (MCP) Server for Mississippi Early Intervention Referral Graph.

Exposes tools and resources over the MCP standard protocol (SSE and stdio).
Allows any MCP-compatible agent or client (Google ADK McpToolset, Claude Desktop, Cursor)
to execute ISO GQL graph queries, triage routing, bounce hub isolation, and equity audits.
"""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

from agent.config import config
from agent.subagents.triage_agent import route_toddler_referral
from agent.subagents.network_audit_agent import (
    diagnose_multi_hop_breaches,
    detect_bounce_hubs,
    simulate_hub_fix,
)
from agent.subagents.equity_screening_agent import run_census_tract_equity_audit
from agent.main_agent import coordinator_service

# Initialize FastMCP Server
mcp = FastMCP(
    name="FirstMilestones-ReferralGraph-MCP",
    instructions=(
        f"MCP Server connected to BigQuery dataset {config.bq_dataset} "
        f"for Mississippi ({config.state_code}) IDEA Part C 45-day statutory clock routing, "
        "multi-hop referral bottleneck detection, and equity auditing."
    ),
)


@mcp.tool(
    name="trace_referral_bounce_loop",
    description=(
        "Traverses multi-hop referral chains (2..4 hops) using ISO GQL "
        "(GRAPH a4i_early_intervention.ReferralGraph MATCH (c:CareNode)-[hops:ReferralHandoff]->{2,4}(v:CareNode)) "
        "with case_chain_id correlation to diagnose paper-fax bottlenecks exceeding the 45-day IDEA Part C limit."
    ),
)
def mcp_trace_referral_bounce_loop(case_chain_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Traces multi-hop referral chains and returns wait times and transmission channels."""
    breaches = diagnose_multi_hop_breaches()
    if case_chain_id:
        return [b for b in breaches if b.get("chain_id") == case_chain_id]
    return breaches


@mcp.tool(
    name="find_compliant_45day_pathway",
    description=(
        "Discovers an optimal <=45-day compliant referral pathway for an incoming toddler matching age, "
        "home tract GEOID, Medicaid enrollment, and Spanish bilingual evaluation needs."
    ),
)
def mcp_find_compliant_45day_pathway(
    child_age_months: int = 22,
    home_tract_geoid: str = "28133950100",
    primary_language: str = "Spanish",
    medicaid_enrolled: bool = True,
) -> Dict[str, Any]:
    """Finds compliant provider sequence: Clinic -> Intake Coordinator -> Eval Hub -> Therapy Vendor."""
    return route_toddler_referral(
        child_age_months=child_age_months,
        home_tract_geoid=home_tract_geoid,
        primary_language=primary_language,
        medicaid_enrolled=medicaid_enrolled,
    )


@mcp.tool(
    name="diagnose_bounce_hubs",
    description=(
        "Isolates regional coordinator hubs (e.g. SYN-PROV-MS-012) where deceptively low internal "
        "wait times (e.g. 5 days) conceal 70+ day multi-hop re-referrals in flat spreadsheets."
    ),
)
def mcp_diagnose_bounce_hubs() -> List[Dict[str, Any]]:
    """Identifies coordinator bounce hubs and calculates cumulative delayed child-days."""
    return detect_bounce_hubs()


@mcp.tool(
    name="simulate_counterfactual_network_fix",
    description=(
        "Simulates upgrading a paper-fax intake hub to an electronic e-referral portal, "
        "calculating total delayed child-days saved and statutory compliance uplift."
    ),
)
def mcp_simulate_counterfactual_network_fix(
    hub_id: str = "SYN-PROV-MS-012",
    intervention_type: str = "e_referral_upgrade",
) -> Dict[str, Any]:
    """Runs counterfactual simulation of upgrading paper fax to e-referral."""
    return simulate_hub_fix(hub_id=hub_id, intervention_type=intervention_type)


@mcp.tool(
    name="run_equity_audit",
    description=(
        "Audits Census tract disparities, poverty rates, zero-vehicle transit friction, "
        "and resolves the zero-column and statewide grain data traps."
    ),
)
def mcp_run_equity_audit() -> Dict[str, Any]:
    """Runs post-output equity audit across breached Census tracts."""
    return run_census_tract_equity_audit()


@mcp.tool(
    name="generate_45_day_brief",
    description=(
        "Compiles the complete 5-part 45-Day Pathway & Bottleneck Brief for Mississippi IDEA Part C: "
        "1. Prospective Routing, 2. ISO GQL Traversal, 3. Bounce Hub Fix, 4. Equity Audit, 5. Bilingual Caregiver Notes."
    ),
)
def mcp_generate_45_day_brief(
    child_age_months: int = 22,
    home_tract_geoid: str = "28133950100",
    primary_language: str = "Spanish",
    medicaid_enrolled: bool = True,
    family_name: str = "Ramirez",
    child_name: str = "Mateo",
) -> Dict[str, Any]:
    """Generates the full official 5-part brief."""
    return coordinator_service.generate_45_day_brief(
        child_age_months=child_age_months,
        home_tract_geoid=home_tract_geoid,
        primary_language=primary_language,
        medicaid_enrolled=medicaid_enrolled,
        family_name=family_name,
        child_name=child_name,
    )


@mcp.resource("referral://standards/idea-part-c")
def get_idea_part_c_standards() -> str:
    """Returns statutory IDEA Part C 45-day timeline and equity compliance rules."""
    return """
INDIVIDUALS WITH DISABILITIES EDUCATION ACT (IDEA) - PART C (34 CFR § 303.310)
1. 45-Day Statutory Clock: From referral date, lead agency has 45 calendar days to complete
   multidisciplinary evaluation and convene the initial IFSP meeting.
2. Language & Cultural Equity: Evaluations must be conducted in the family's native language.
3. Medicaid Rights: Part C evaluations and service coordination are free to families.
4. Age Cliff: At 36 months, toddlers age out of Part C and must transition to Part B preschool.
"""


@mcp.resource("bigquery://dataset/a4i_early_intervention")
def get_bigquery_dataset_resource() -> str:
    """Returns BigQuery connection metadata and Property Graph reference."""
    return f"""
BigQuery Project: {config.project_id}
BigQuery Dataset: {config.bq_dataset}
State: {config.state_code} (FIPS {config.state_fips})
Property Graph: CREATE OR REPLACE PROPERTY GRAPH {config.bq_dataset}.ReferralGraph
CareNode Vertices: {config.bq_dataset}.pediatric_and_ei_provider_directory
ReferralHandoff Edges: {config.bq_dataset}.deidentified_part_c_referral_logs
Demographics: {config.bq_dataset}.acs_under5_tract_demographics
"""


if __name__ == "__main__":
    mcp.run()
