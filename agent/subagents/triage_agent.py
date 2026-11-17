"""Triage and Routing Subagent for Today's Toddler Referral (Track 1)."""

from google.adk.agents import LlmAgent
from agent.config import config
from agent.tools.routing_tools import RoutingTools


def route_toddler_referral(
    child_age_months: int,
    home_tract_geoid: str,
    primary_language: str = "Spanish",
    medicaid_enrolled: bool = True,
) -> dict:
    """Tool to search BigQuery property graph candidates and find a compliant <=45-day route.

    Args:
        child_age_months: Age of the infant or toddler in months (0-35).
        home_tract_geoid: 11-character US Census tract GEOID (e.g. '28133950100').
        primary_language: Family's primary home language (e.g. 'Spanish', 'English').
        medicaid_enrolled: Whether child relies on Medicaid coverage.

    Returns:
        A dictionary containing the validated <=45-day pathway and statutory margins.
    """
    return RoutingTools.find_compliant_pathway(
        child_age_months=child_age_months,
        home_tract_geoid=home_tract_geoid,
        primary_language=primary_language,
        medicaid_enrolled=medicaid_enrolled,
    )


TRIAGE_INSTRUCTION = """You are the Early Intervention Triage Specialist for Mississippi IDEA Part C.
Your mandate is to route an active infant or toddler referral to a fully compliant provider sequence
(Screening Clinic -> Part C Intake Coordinator -> Multidisciplinary Evaluation Hub -> EI Therapy Vendor)
that clears the federal 45-day statutory clock under IDEA Part C.

Key Rules:
1. Enforce the statutory ceiling: Cumulative wait must be <= 45 calendar days.
2. Verify Provider Eligibility: The evaluation center and therapy vendor must accept Medicaid and list bilingual capabilities when required.
3. Guard against the 36-month age-out cliff: Children >= 30 months must be flagged with urgent priority.
4. Avoid historical bounce hubs: Do not route through intake coordinators using paper_fax handoffs to non-Medicaid centers.
5. Emphasize that all provider entities (SYN-PROV-*) are 100% synthetic for privacy.
"""


def create_triage_agent() -> LlmAgent:
    """Creates the ADK LlmAgent for Active Toddler Routing."""
    return LlmAgent(
        name="TriageRoutingAgent",
        description="Routes active toddler referrals to compliant <=45-day provider pathways under IDEA Part C.",
        model=config.model_name,
        instruction=TRIAGE_INSTRUCTION,
        tools=[route_toddler_referral],
    )


TriageAgent = create_triage_agent()
