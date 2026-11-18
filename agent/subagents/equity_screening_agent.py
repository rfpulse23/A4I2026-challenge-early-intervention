"""Equity Audit and Community Screening Subagent (Track 3)."""

from google.adk.agents import LlmAgent
from agent.config import config
from agent.tools.equity_tools import EquityTools


def run_census_tract_equity_audit() -> dict:
    """Audits demographic disparities and transit barriers in Census tracts experiencing >45-day referral breaches."""
    return EquityTools.run_equity_audit()


EQUITY_INSTRUCTION = """You are the Equity and Community Screening Coordinator for Mississippi Early Intervention.
Your mandate is to evaluate neighborhood disparities in 45-day statutory breaches and prioritize mobile
screening days in high-poverty, zero-vehicle Census tracts with validated downstream capacity.

Key Disciplines:
1. Avoid planted data traps:
   - Catch that limited_english_rate is 0.0 across the ACS extract (use NSCH language strata & provider bilingual_services_listed).
   - Avoid joining NSCH developmental survey on state_code alone, which duplicates tracts 6x.
2. Analyze transit friction: Address high no_vehicle_rate (22-28%) in breached tracts (e.g. Sunflower & Washington counties)
   by recommending transit-accessible or mobile screening sites without using race as a routing input.
3. Verify downstream capacity: Never schedule screening days without verifying that local intake paths clear <= 45 days.
"""


def create_equity_screening_agent() -> LlmAgent:
    """Creates the ADK LlmAgent for Equity Audits and Community Screening."""
    return LlmAgent(
        name="EquityScreeningAgent",
        description="Analyzes Census tract demographic disparities, zero-vehicle barriers, and screening priorities.",
        model=config.model_name,
        instruction=EQUITY_INSTRUCTION,
        tools=[run_census_tract_equity_audit],
    )


EquityScreeningAgent = create_equity_screening_agent()
