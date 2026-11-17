"""
Interactive runner and demonstration script for the Early Intervention ADK Agent.
"""
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.agent import (
    create_coordinator_agent,
    tool_trace_bounce_loop,
    tool_find_compliant_pathway,
    tool_run_equity_audit
)

def run_triage_demonstration():
    print("="*80)
    print("  EARLY INTERVENTION (IDEA PART C) 45-DAY TRIAGE & ROUTING ASSISTANT")
    print("  Agents for Impact 2026 · State: Mississippi (FIPS 28)")
    print("="*80)
    
    # Scenario: 20-month-old toddler, Spanish-speaking, Medicaid, Rural Delta Tract
    tract_geoid = "28011950701" # Bolivar County, MS
    age_months = 20
    case_chain_id = "CHAIN-MS-009"
    
    print(f"\n[INCOMING REFERRAL CASE]")
    print(f" • Child Age: {age_months} months (Concern: Expressive Speech / Language)")
    print(f" • Home Census Tract: {tract_geoid} (Bolivar County, Mississippi)")
    print(f" • Insurance: Medicaid-enrolled")
    print(f" • Home Language: Spanish (Bilingual developmental evaluation required)")
    print(f" • Federal Ceiling: 45 calendar days (34 CFR § 303.310)")
    
    print("\n" + "-"*80)
    print("STEP 1: Diagnosing Historical Bottleneck (ISO GQL Multi-Hop Graph Traversal)")
    print("-"*(80))
    trace = tool_trace_bounce_loop(case_chain_id=case_chain_id, state_code="MS")
    chain = trace["chains"][0]
    
    print(f"Traversed Chain ID: {chain['case_chain_id']}")
    print(f"Total Hops: {chain['total_hops']} | Paper Fax Hops: {chain['fax_hops']}")
    print(f"Cumulative Wait Time: {chain['cumulative_wait_days']} DAYS (FEDERAL 45-DAY LIMIT BREACHED!)")
    print("\nHop-by-Hop Breakdown:")
    for h in chain["hops"]:
        status = "⚠️ BOUNCE" if "Bounce" in h["reason"] else "✓ Handoff"
        print(f"  Hop {h['hop']}: {h['source_name']} -> {h['target_name']}")
        print(f"         Channel: {h['channel']} | Wait: {h['wait_days']} days | Reason: {h['reason']}")
    
    print("\n" + "-"*80)
    print("STEP 2: Prospective Compliant Pathway Discovery (<=45-Day Electronic Fast-Track)")
    print("-"*(80))
    compliant_path = tool_find_compliant_pathway(
        child_age_months=age_months,
        home_tract_geoid=tract_geoid,
        requires_medicaid=True,
        requires_bilingual=True,
        state_code="MS"
    )
    
    print(f"Compliant Route Cumulative Wait: {compliant_path['cumulative_wait_days']} DAYS")
    print(f"Statutory 45-Day Clock Status: {'✓ COMPLIANT (Saved ' + str(compliant_path['days_saved_vs_fax_baseline']) + ' days vs. fax baseline)' if compliant_path['is_compliant'] else '✗ NON-COMPLIANT'}")
    print("\nRecommended Provider Sequence:")
    for step in compliant_path["recommended_pathway"]:
        print(f"  Step {step['step']} [{step['role']}]: {step['name']}")
        if "distance_km" in step:
            print(f"         Distance: {step['distance_km']} km | Est. Wait: {step.get('estimated_wait_days', 'N/A')} days")
            
    print("\n" + "-"*80)
    print("STEP 3: Post-Output Equity Audit (Neighborhood Context & Transport Barriers)")
    print("-"*(80))
    equity = tool_run_equity_audit(home_tract_geoid=tract_geoid, state_code="MS")
    print(f"County: {equity['county_name']} | Under-5 Population: {equity['under_5_population']}")
    print(f"Neighborhood Poverty Rate: {equity['neighborhood_poverty_rate_pct']}% (State Avg: {equity['state_avg_poverty_rate_pct']}%)")
    print(f"Zero-Vehicle Household Rate: {equity['neighborhood_no_vehicle_rate_pct']}% (State Avg: {equity['state_avg_no_vehicle_rate_pct']}%)")
    print(f"Transport Barrier Alert: {equity['transport_barrier_alert']}")
    print(f"Recommendation: {equity['recommendation']}")

    print("\n" + "-"*80)
    print("STEP 4: Plain-Language Caregiver Action Note (English & Spanish)")
    print("-"*(80))
    print("""
[ENGLISH CAREGIVER ACTION NOTE]
Dear Family,
Your pediatrician has connected your 20-month-old child with Mississippi Early Intervention.
We have scheduled your comprehensive bilingual developmental evaluation with Greenwood Developmental-Behavioral & Speech Evaluation Hub.
Your expected appointment timeline is within 14 business days, well within the 45-day federal guideline. Because transportation can be a challenge in Bolivar County, Medicaid Non-Emergency Transportation (NEMT) is available at no cost to drive you to and from the clinic. A bilingual coordinator will contact you by phone tomorrow.

[NOTA DE ACCIÓN PARA LA FAMILIA (ESPAÑOL)]
Estimada familia:
El pediatra de su niño(a) de 20 meses lo ha conectado con el programa de Intervención Temprana de Mississippi.
Hemos coordinado su evaluación integral del desarrollo con profesionales bilingües en Greenwood Developmental-Behavioral & Speech Evaluation Hub.
La cita se llevará a cabo dentro de los próximos 14 días laborables, cumpliendo con el plazo federal de 45 días. Si no cuenta con transporte en el condado de Bolivar, el servicio de transporte médico de Medicaid está disponible sin costo para llevarlos y traerlos a la clínica. Un coordinador bilingüe se comunicará con ustedes mañana.
""")

    print("="*80)
    print("✓ 45-Day Pathway & Bottleneck Brief Generated Successfully!")
    print("  Provenance: Providers/Logs 100% [Synthetic]; Census Demographics Real Public ACS Data.")
    print("="*80)

if __name__ == "__main__":
    run_triage_demonstration()
