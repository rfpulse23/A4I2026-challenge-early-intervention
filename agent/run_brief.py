"""CLI Demonstration Runner: Generates the 45-Day Pathway & Bottleneck Brief."""

import json
from agent.main_agent import coordinator_service


def main():
    print("=" * 80)
    print("FIRST MILESTONES — EARLY INTERVENTION & DEVELOPMENTAL SCREENING TRIAGE (MS)")
    print("Agents for Impact 2026")
    print("=" * 80)

    # Sample Incoming Referral: 22-month-old Mateo Ramirez from Sunflower County, MS (Tract 28133950100)
    brief = coordinator_service.generate_45_day_brief(
        child_age_months=22,
        home_tract_geoid="28133950100",
        primary_language="Spanish",
        medicaid_enrolled=True,
        family_name="Ramirez",
        child_name="Mateo",
    )

    print("\n[DECLARATION]")
    print(brief["synthetic_data_declaration"])

    print("\n" + "=" * 80)
    print("1. PROSPECTIVE ROUTING: RECOMMENDED <=45-DAY PATHWAY FOR TODAY'S TODDLER")
    print("=" * 80)
    p = brief["1_prospective_triage_pathway"]["recommended_pathway"]
    print(f"Child: Mateo Ramirez (22 months) | Home Tract: 28133950100 | Language: Spanish | Medicaid: Yes")
    print(f"Statutory Clock Limit : 45 calendar days")
    print(f"Total Cumulative Wait : {p['total_cumulative_wait_days']} days (Margin: +{p['statutory_margin_days']} days)")
    print("\nTraced Sequence:")
    print(f"  Hop 1: {p['hop_1']['source']} -> {p['hop_1']['target']}")
    print(f"         Channel: {p['hop_1']['channel']} | Wait: {p['hop_1']['wait_days']} days")
    print(f"  Hop 2: {p['hop_2']['source']} -> {p['hop_2']['target']}")
    print(f"         Channel: {p['hop_2']['channel']} | Wait: {p['hop_2']['wait_days']} days [Spanish & Medicaid Verified]")
    print(f"  Hop 3: {p['hop_3']['source']} -> {p['hop_3']['target']}")
    print(f"         Channel: {p['hop_3']['channel']} | Wait: {p['hop_3']['wait_days']} days [Part C Enrolled Vendor]")

    print("\n" + "=" * 80)
    print("2. HISTORICAL DIAGNOSIS: VARIABLE-LENGTH ISO GQL TRAVERSAL (-{2,4}->)")
    print("=" * 80)
    diag = brief["2_historical_iso_gql_diagnosis"]
    print(f"ISO GQL Pattern: {diag['traversal_pattern']}")
    print(f"Correlation Rule: {diag['correlation_rule']}")
    print("\nDiagnosed Breached Referral Chains (Exceeding 45 Days):")
    for chain in diag["diagnosed_breaches"]:
        print(f"  - Chain {chain['chain_id']}: {chain['total_hops']} hops | {chain['chain_wait_days']} days ({chain['fax_hops']} fax hops)")
        print(f"    Origin: {chain['origin_clinic']} -> Coordinator: {chain['intake_coord_id']} -> Final: {chain['final_vendor']}")
        print(f"    Diagnosis: {chain.get('breach_notes', 'Paper fax bounce.')}")

    print("\n" + "=" * 80)
    print("3. REGIONAL BOUNCE HUB DIAGNOSIS & COUNTERFACTUAL POLICY INTERVENTION")
    print("=" * 80)
    hub = brief["3_regional_bounce_hub_and_fix"]["bounce_hub_diagnosis"]
    cf = brief["3_regional_bounce_hub_and_fix"]["counterfactual_simulation"]
    print(f"Bounce Hub Detected : {hub.get('coordinator_name')} ({hub.get('coordinator_id')})")
    print(f"Internal Wait Time  : {hub.get('coordinator_internal_wait_days')} days [Appears healthy in flat spreadsheet!]")
    print(f"Breached Chains     : Involved in {hub.get('breached_chains_involved')} multi-hop breaches (Avg Wait: {hub.get('avg_breached_chain_wait_days')} days)")
    print(f"Root Cause          : {hub.get('root_cause')}")
    print(f"\nCounterfactual Simulation:")
    print(f"  Intervention      : {cf.get('intervention')}")
    print(f"  Child-Days Saved  : {cf.get('total_child_days_saved_annually')} child-days annually")
    print(f"  Regional Impact   : {cf.get('recommendation')}")

    print("\n" + "=" * 80)
    print("4. POST-OUTPUT EQUITY AUDIT (CENSUS TRACT DISPARITIES & TRANSIT FRICTION)")
    print("=" * 80)
    ea = brief["4_post_output_equity_audit"]
    print("Neighborhoods Bearing the Brunt of Multi-Hop Breaches:")
    for rec in ea["equity_audit_records"][:3]:
        print(f"  - Tract {rec['census_tract_geoid']} ({rec['county_name']}):")
        print(f"    Poverty Rate: {rec['poverty_rate']*100:.1f}% | Zero-Vehicle Households: {rec['no_vehicle_rate']*100:.1f}%")
        print(f"    Demographics: {rec['audit_black_share']*100:.1f}% Black, {rec['audit_hispanic_share']*100:.1f}% Hispanic")
        print(f"    Breaches: {rec['breached_referral_count']} chains | Avg Wait: {rec['avg_breached_wait_days']} days")
    print("\nData Trap Guardrails Applied:")
    for dt in ea["data_traps_guardrails_applied"]:
        print(f"  - {dt['trap']}: {dt['resolution']}")
    print(f"\nTransit Barrier Note: {ea['transit_barrier_finding']}")

    print("\n" + "=" * 80)
    print("5. BILINGUAL CAREGIVER ACTION NOTES (ENGLISH & SPANISH)")
    print("=" * 80)
    cg = brief["5_bilingual_caregiver_note"]
    print("--- ENGLISH NOTE ---")
    print(cg["english_action_note"])
    print("\n--- SPANISH NOTE ---")
    print(cg["spanish_action_note"])
    print("=" * 80)


if __name__ == "__main__":
    main()
