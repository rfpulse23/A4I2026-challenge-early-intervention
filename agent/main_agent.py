"""Root ADK Orchestrator Agent: First Milestones Early Intervention Coordinator."""

from typing import Any, Dict, Optional
from google.adk.agents import LlmAgent
from agent.config import config
from agent.subagents.triage_agent import TriageAgent, route_toddler_referral
from agent.subagents.network_audit_agent import (
    NetworkAuditAgent,
    diagnose_multi_hop_breaches,
    detect_bounce_hubs,
    simulate_hub_fix,
)
from agent.subagents.equity_screening_agent import EquityScreeningAgent, run_census_tract_equity_audit
from agent.subagents.caregiver_comms_agent import CaregiverCommsAgent, format_caregiver_action_note


COORDINATOR_INSTRUCTION = """You are the First Milestones Lead Coordinator for Mississippi IDEA Part C Early Intervention.
You oversee the multi-agent Early Intervention triage and network-audit assistant.

Your mandate is to produce the official '45-Day Pathway & Bottleneck Brief' whenever an incoming referral
is evaluated or a network audit is requested.

Every generated Brief MUST contain the five core deliverables:
1. Visual / Traced Multi-Hop Path (Hop 1 -> Hop 2 -> Hop 3, wait days, and cumulative count against 45-day federal ceiling).
2. Compliant <=45-Day Provider Sequence (Medicaid, Spanish bilingual, Part C vendor verified).
3. Top Regional Bounce Hub Diagnosis (highlighting Coordinator Hub SYN-PROV-MS-012 and counterfactual child-days saved).
4. Post-Output Equity Audit Summary (Census tract poverty & no-vehicle rates, reporting resolution of ACS zero-column trap).
5. Plain-Language Caregiver Action Note (in English and Spanish).

State clearly that all provider organizations and referral records are 100% [Synthetic] to protect clinician identities.
"""


class FirstMilestonesCoordinatorService:
    """Service orchestrating specialized tools and subagents to produce the 45-Day Brief."""

    def __init__(self):
        self.agent = LlmAgent(
            name="FirstMilestonesCoordinator",
            description="Chief Early Intervention Triage and Network-Audit Assistant for Mississippi IDEA Part C.",
            model=config.model_name,
            instruction=COORDINATOR_INSTRUCTION,
            sub_agents=[
                TriageAgent,
                NetworkAuditAgent,
                EquityScreeningAgent,
                CaregiverCommsAgent,
            ],
            tools=[
                route_toddler_referral,
                diagnose_multi_hop_breaches,
                detect_bounce_hubs,
                simulate_hub_fix,
                run_census_tract_equity_audit,
                format_caregiver_action_note,
            ],
        )

    def generate_45_day_brief(
        self,
        child_age_months: int = 22,
        home_tract_geoid: str = "28133950100",
        primary_language: str = "Spanish",
        medicaid_enrolled: bool = True,
        family_name: str = "Ramirez",
        child_name: str = "Mateo",
    ) -> Dict[str, Any]:
        """Synthesizes all subagents' analyses into the final 45-Day Pathway & Bottleneck Brief."""
        # 1. Prospective Triage & Routing
        routing_result = route_toddler_referral(
            child_age_months=child_age_months,
            home_tract_geoid=home_tract_geoid,
            primary_language=primary_language,
            medicaid_enrolled=medicaid_enrolled,
        )

        # 2. Historical Breach Diagnosis via ISO GQL
        historical_breaches = diagnose_multi_hop_breaches()

        # 3. Bounce Hub Isolation & Counterfactual Upgrade
        bounce_hubs = detect_bounce_hubs()
        top_hub = bounce_hubs[0] if bounce_hubs else {}
        counterfactual_fix = simulate_hub_fix(
            coordinator_id=top_hub.get("coordinator_id", "SYN-PROV-MS-012"),
            intervention_type="e_referral_upgrade",
        )

        # 4. Post-Output Equity Audit
        equity_audit = run_census_tract_equity_audit()

        # 5. Caregiver Action Note (Bilingual)
        path = routing_result.get("recommended_pathway", {})
        caregiver_note = format_caregiver_action_note(
            family_name=family_name,
            child_name=child_name,
            origin_clinic=path.get("hop_1", {}).get("source", "Delta Rural Child Health Initiative [Synthetic]"),
            intake_coordinator=path.get("hop_2", {}).get("source", "Mid-Delta Regional Part C Services [Synthetic]"),
            eval_center=path.get("hop_2", {}).get("target", "Greenwood Multidisciplinary Developmental Center [Synthetic]"),
            therapy_vendor=path.get("hop_3", {}).get("target", "Leflore Comprehensive Speech & Motor Therapy [Synthetic]"),
            total_expected_days=path.get("total_cumulative_wait_days", 34),
            primary_language=primary_language,
        )

        return {
            "title": "45-Day Pathway & Bottleneck Brief — Mississippi IDEA Part C Early Intervention",
            "state": "Mississippi (MS, FIPS 28)",
            "synthetic_data_declaration": (
                "Notice: All provider organizations (SYN-PROV-*), Part C agencies (SYN-PARTC-*), and referral log rows "
                "are 100% [Synthetic] to protect clinician identities, while Census under-5 demographics are real ACS tract data."
            ),
            "1_prospective_triage_pathway": routing_result,
            "2_historical_iso_gql_diagnosis": {
                "traversal_pattern": "GRAPH a4i_early_intervention.ReferralGraph MATCH (c:CareNode)-[hops:ReferralHandoff]->{2,4}(v:CareNode)",
                "correlation_rule": "(SELECT COUNT(DISTINCT h.case_chain_id) FROM UNNEST(hops) AS h) = 1",
                "diagnosed_breaches": historical_breaches,
            },
            "3_regional_bounce_hub_and_fix": {
                "bounce_hub_diagnosis": top_hub,
                "counterfactual_simulation": counterfactual_fix,
            },
            "4_post_output_equity_audit": equity_audit,
            "5_bilingual_caregiver_note": caregiver_note,
        }


coordinator_service = FirstMilestonesCoordinatorService()
root_agent = coordinator_service.agent
