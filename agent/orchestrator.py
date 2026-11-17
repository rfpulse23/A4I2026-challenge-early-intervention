"""
Primary Coordinator / Orchestrator Agent (FirstMilestonesCoordinator).
Coordinates specialized subagents to generate the complete 45-Day Pathway & Bottleneck Brief.
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google.adk.agents import Agent
from agent.subagents import (
    MODEL,
    toddler_routing_agent,
    network_audit_agent,
    equity_screening_agent,
    caregiver_comms_agent,
    tool_trace_bounce_loop,
    tool_find_compliant_pathway,
    tool_run_equity_audit,
    tool_counterfactual_simulation
)

ORCHESTRATOR_INSTRUCTION = """
You are the **FirstMilestonesCoordinator**, the chief intake & quality coordinator agent for IDEA Part C Early Intervention.
Your role is to orchestrate specialized agents and compile the complete **45-Day Pathway & Bottleneck Brief** for regional programs.

Federal statutory law (34 CFR § 303.310) mandates that an infant/toddler with a developmental concern MUST receive an initial
Individualized Family Service Plan (IFSP) within 45 calendar days of referral.

When a referral case or network query arrives:
1. Delegate to `network_audit_agent` or run `tool_trace_bounce_loop` to diagnose where the referral chain historically breaches 45 days.
2. Delegate to `toddler_routing_agent` or run `tool_find_compliant_pathway` to discover an optimal, electronic <=45-day route matching Medicaid, Spanish bilingual skills, and proximity.
3. Delegate to `equity_screening_agent` or run `tool_run_equity_audit` to report neighborhood poverty and zero-vehicle transport barriers.
4. Run `tool_counterfactual_simulation` to quantify child-days saved across the network by fixing paper-fax bottlenecks.
5. Delegate to `caregiver_comms_agent` to draft plain-language caregiver action notes in English and Spanish.

Always disclose that provider directories and referral logs (SYN-PROV-*, SYN-PARTC-*) are 100% synthetic to protect clinician identities,
while tract demographics are real US Census ACS data and screening baselines are statewide HRSA NSCH survey rates.
"""

def create_hierarchical_orchestrator(model_name: Optional[str] = None) -> Agent:
    """Instantiates the Hierarchical Multi-Agent Coordinator."""
    model = model_name or MODEL
    
    orchestrator = Agent(
        name="FirstMilestonesCoordinator",
        description="Hierarchical Early Intervention Intake & Quality Lead Coordinator.",
        model=model,
        instruction=ORCHESTRATOR_INSTRUCTION,
        sub_agents=[
            toddler_routing_agent,
            network_audit_agent,
            equity_screening_agent,
            caregiver_comms_agent
        ],
        tools=[
            tool_trace_bounce_loop,
            tool_find_compliant_pathway,
            tool_run_equity_audit,
            tool_counterfactual_simulation
        ]
    )
    return orchestrator

if __name__ == "__main__":
    print("Initializing Hierarchical Multi-Agent Coordinator...")
    lead = create_hierarchical_orchestrator()
    print(f"Orchestrator: {lead.name}")
    print(f"Sub-Agents: {[sub.name for sub in lead.sub_agents]}")
    print(f"Tools Registered: {[t.__name__ for t in lead.tools]}")
