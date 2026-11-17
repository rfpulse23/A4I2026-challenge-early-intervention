"""Network Audit and Bottleneck Subagent for Quarterly Audits (Track 2)."""

from google.adk.agents import LlmAgent
from agent.config import config
from agent.tools.graph_tools import GraphTools
from agent.tools.audit_tools import AuditTools


def diagnose_multi_hop_breaches(min_hops: int = 3, min_wait_days: int = 45) -> list:
    """Traverses historical referral chains in ReferralGraph using ISO GQL to find >45-day breaches.

    Args:
        min_hops: Minimum hops to traverse (default 3).
        min_wait_days: Statutory threshold (default 45).

    Returns:
        List of multi-hop referral chains breaching federal law.
    """
    return GraphTools.diagnose_historical_breaches(min_hops=min_hops, min_wait_days=min_wait_days)


def detect_bounce_hubs() -> list:
    """Isolates intake coordinators with low internal wait times that trigger multi-hop referral breaches."""
    return AuditTools.identify_bounce_hubs()


def simulate_hub_fix(coordinator_id: str, intervention_type: str = "e_referral_upgrade") -> dict:
    """Simulates counterfactual child-days saved if a specific intake hub upgrades its handoff protocol.

    Args:
        coordinator_id: The synthetic coordinator ID (e.g. 'SYN-PROV-MS-012').
        intervention_type: Intervention type (e.g. 'e_referral_upgrade', 'bilingual_staffing').
    """
    return AuditTools.simulate_counterfactual_intervention(coordinator_id, intervention_type)


AUDIT_INSTRUCTION = """You are the Quality Lead and Network Audit Specialist for Mississippi IDEA Part C.
Your mandate is to use BigQuery Property Graphs (ISO GQL) to expose hidden referral bottlenecks
breaking the 45-day statutory ceiling across the provider network.

Key Principles:
1. A flat SQL sort on provider waitlists points only at busy downstream clinics (symptoms at hop 2/3).
2. You must traverse variable-length graph paths (-{2,4}->) correlated on case_chain_id to uncover root causes.
3. Expose Coordinator Hub SYN-PROV-MS-012: It appears fast in flat tables (median_internal_wait_days = 5),
   yet its paper_fax handoffs to non-bilingual / non-Medicaid centers trigger multi-hop bounce breaches (>70 days).
4. Quantify counterfactual impact: Calculate how many delayed child-days are saved by upgrading paper fax to e-referral.
"""


def create_network_audit_agent() -> LlmAgent:
    """Creates the ADK LlmAgent for Network Bottleneck Audits."""
    return LlmAgent(
        name="NetworkAuditAgent",
        description="Audits multi-hop graph referral logs using ISO GQL to isolate bounce hubs and quantify policy fixes.",
        model=config.model_name,
        instruction=AUDIT_INSTRUCTION,
        tools=[diagnose_multi_hop_breaches, detect_bounce_hubs, simulate_hub_fix],
    )


NetworkAuditAgent = create_network_audit_agent()
