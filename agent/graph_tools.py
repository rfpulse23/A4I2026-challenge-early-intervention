"""agent/graph_tools.py

Data and Graph tools for Early Intervention & Developmental Screening Triage.
Provides the ADK Agent with callable functions that execute BigQuery Property Graph
traversals (ISO GQL), spatial accessibility checks, and post-output equity audits.
"""

from typing import Any, Dict, List, Optional
from google.cloud import bigquery


def get_bigquery_client(project_id: Optional[str] = None) -> bigquery.Client:
    """Returns an initialized BigQuery Client."""
    return bigquery.Client(project=project_id)


def diagnose_historical_breaches(
    project_id: str,
    dataset_id: str = "a4i_early_intervention",
    min_hops: int = 3,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Diagnoses multi-hop referral chains breaching the federal 45-day Part C ceiling.

    Executes variable-length ISO GQL traversals on ReferralGraph to expose
    bottleneck intake coordinators relying on paper fax.
    """
    client = get_bigquery_client(project_id)
    query = f"""
    GRAPH `{project_id}.{dataset_id}.ReferralGraph`
    MATCH (clinic:CareNode {{node_role: 'Screening_Pediatric_Clinic'}})
          -[hops:ReferralHandoff]->{{2,4}}
          (vendor:CareNode {{node_role: 'EI_Therapy_Vendor'}})
    WHERE ARRAY_LENGTH(hops) >= {min_hops}
      AND (SELECT COUNT(DISTINCT h.case_chain_id) FROM UNNEST(hops) AS h) = 1
    LET total_hops = ARRAY_LENGTH(hops),
        chain_id = hops[OFFSET(0)].case_chain_id,
        chain_wait_days = (SELECT SUM(h.handoff_wait_days) FROM UNNEST(hops) AS h),
        fax_hops = (SELECT COUNTIF(h.transmission_channel = 'paper_fax') FROM UNNEST(hops) AS h)
    FILTER chain_wait_days > 45
    RETURN
      chain_id,
      clinic.synthetic_organization_name AS origin_clinic,
      hops[OFFSET(0)].target_provider_id AS coordinator_id,
      vendor.synthetic_organization_name AS final_vendor,
      total_hops,
      fax_hops,
      chain_wait_days
    ORDER BY chain_wait_days DESC
    LIMIT {limit};
    """
    results = client.query(query).to_dataframe()
    return results.to_dict(orient="records")


def find_compliant_pathways(
    project_id: str,
    dataset_id: str = "a4i_early_intervention",
    medicaid_required: bool = True,
    bilingual_required: bool = True,
    max_days: int = 45,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Finds active <=45-day multi-hop provider pathways for an incoming referral.

    Filters candidate sequences across Clinic -> Coordinator -> Eval Hub -> Vendor
    matching Medicaid status, language access, and cumulative statutory wait budget.
    """
    client = get_bigquery_client(project_id)
    query = f"""
    GRAPH `{project_id}.{dataset_id}.ReferralGraph`
    MATCH (clinic:CareNode {{node_role: 'Screening_Pediatric_Clinic'}})
          -[h1:ReferralHandoff]-> (coord:CareNode {{node_role: 'Part_C_Intake_Coordinator'}})
          -[h2:ReferralHandoff]-> (eval:CareNode {{node_role: 'Multidisciplinary_Eval_Hub'}})
          -[h3:ReferralHandoff]-> (vendor:CareNode {{node_role: 'EI_Therapy_Vendor'}})
    WHERE (NOT {medicaid_required} OR eval.accepts_medicaid = TRUE)
      AND (NOT {bilingual_required} OR eval.bilingual_services_listed = TRUE)
      AND vendor.vendor_enrolled_in_part_c = TRUE
      AND (h1.handoff_wait_days + h2.handoff_wait_days + h3.handoff_wait_days) <= {max_days}
    RETURN
      clinic.synthetic_organization_name AS clinic_name,
      coord.synthetic_organization_name AS coordinator_name,
      h1.transmission_channel AS hop1_channel,
      h1.handoff_wait_days AS hop1_days,
      eval.synthetic_organization_name AS eval_hub_name,
      h2.transmission_channel AS hop2_channel,
      h2.handoff_wait_days AS hop2_days,
      vendor.synthetic_organization_name AS vendor_name,
      h3.transmission_channel AS hop3_channel,
      h3.handoff_wait_days AS hop3_days,
      (h1.handoff_wait_days + h2.handoff_wait_days + h3.handoff_wait_days) AS total_cumulative_wait_days
    ORDER BY total_cumulative_wait_days ASC
    LIMIT {limit};
    """
    results = client.query(query).to_dataframe()
    return results.to_dict(orient="records")


def check_transit_guardrail(
    tract_geoid: str,
    project_id: str,
    dataset_id: str = "a4i_early_intervention",
) -> Dict[str, Any]:
    """Evaluates zero-vehicle transit barriers between a child's home census tract

    and the nearest bilingual Medicaid evaluation hub.
    """
    client = get_bigquery_client(project_id)
    query = f"""
    SELECT
        census_tract_geoid,
        county_name,
        poverty_pct,
        no_vehicle_pct,
        nearest_bilingual_eval_hub,
        distance_km,
        transit_risk_tier,
        coordinator_action
    FROM `{project_id}.{dataset_id}.tract_transit_guardrails`
    WHERE census_tract_geoid = '{tract_geoid}'
    LIMIT 1;
    """
    rows = list(client.query(query).result())
    if not rows:
        return {
            "census_tract_geoid": tract_geoid,
            "found": False,
            "message": "Census tract not found in tract_transit_guardrails table.",
        }
    r = rows[0]
    return {
        "census_tract_geoid": r.census_tract_geoid,
        "county_name": r.county_name,
        "poverty_pct": r.poverty_pct,
        "no_vehicle_pct": r.no_vehicle_pct,
        "nearest_bilingual_eval_hub": r.nearest_bilingual_eval_hub,
        "distance_km": r.distance_km,
        "transit_risk_tier": r.transit_risk_tier,
        "coordinator_action": r.coordinator_action,
        "found": True,
    }


def get_post_output_equity_audit(
    project_id: str,
    dataset_id: str = "a4i_early_intervention",
) -> List[Dict[str, Any]]:
    """Performs the mandated Post-Output Equity Audit comparing demographic and poverty

    indicators between timely (<=45 days) and breached (>45 days) referral episodes.
    """
    client = get_bigquery_client(project_id)
    query = f"""
    WITH chain_totals AS (
        SELECT
            case_chain_id,
            ANY_VALUE(child_home_tract_geoid) AS child_home_tract_geoid,
            SUM(handoff_wait_days) AS episode_wait_days
        FROM `{project_id}.{dataset_id}.deidentified_part_c_referral_logs`
        GROUP BY case_chain_id
    )
    SELECT
        IF(c.episode_wait_days > 45, 'Breached (>45 days)', 'Timely (<=45 days)') AS ifsp_status,
        COUNT(*) AS episodes,
        ROUND(AVG(d.poverty_rate) * 100, 1) AS avg_tract_poverty_pct,
        ROUND(AVG(d.no_vehicle_rate) * 100, 1) AS avg_no_vehicle_pct,
        ROUND(AVG(d.audit_black_share) * 100, 1) AS audit_black_pct,
        ROUND(AVG(d.audit_hispanic_share) * 100, 1) AS audit_hispanic_pct,
        ROUND(AVG(d.audit_white_share) * 100, 1) AS audit_white_pct
    FROM chain_totals AS c
    INNER JOIN `{project_id}.{dataset_id}.acs_under5_tract_demographics` AS d
        ON c.child_home_tract_geoid = d.census_tract_geoid
    GROUP BY 1
    ORDER BY 1;
    """
    results = client.query(query).to_dataframe()
    return results.to_dict(orient="records")


def simulate_counterfactual_fax_upgrade(
    project_id: str,
    dataset_id: str = "a4i_early_intervention",
    simulated_ehr_wait_days: int = 4,
) -> Dict[str, Any]:
    """Simulates the network-wide effect of eliminating paper fax handoffs.

    Calculates how many statutory 45-day breaches drop into compliance and the
    net cumulative child-days recovered when intake coordinators switch to
    electronic portal transmissions.
    """
    client = get_bigquery_client(project_id)
    query = f"""
    WITH simulation AS (
        SELECT
            case_chain_id,
            SUM(handoff_wait_days) AS baseline_wait_days,
            SUM(IF(transmission_channel = 'paper_fax', {simulated_ehr_wait_days}, handoff_wait_days)) AS simulated_wait_days
        FROM `{project_id}.{dataset_id}.deidentified_part_c_referral_logs`
        GROUP BY case_chain_id
    )
    SELECT
        COUNT(*) AS total_episodes,
        COUNTIF(baseline_wait_days > 45) AS baseline_breaches,
        COUNTIF(simulated_wait_days <= 45 AND baseline_wait_days > 45) AS cases_recovered_to_compliance,
        ROUND(COUNTIF(simulated_wait_days <= 45 AND baseline_wait_days > 45) * 100.0 / COUNTIF(baseline_wait_days > 45), 1) AS recovery_rate_pct,
        SUM(baseline_wait_days - simulated_wait_days) AS total_child_days_saved
    FROM simulation;
    """
    rows = list(client.query(query).result())
    r = rows[0]
    return {
        "total_episodes": r.total_episodes,
        "baseline_breaches": r.baseline_breaches,
        "cases_recovered_to_compliance": r.cases_recovered_to_compliance,
        "recovery_rate_pct": r.recovery_rate_pct,
        "total_child_days_saved": r.total_child_days_saved,
    }


def evaluate_age_out_risk(child_age_months: int) -> Dict[str, Any]:
    """Classifies Part C age-out risk against the statutory 36-month program exit.

    Children referred at 30+ months face high risk of aging out before receiving
    services, requiring accelerated evaluations and concurrent Part B preschool outreach.
    """
    if child_age_months >= 32:
        return {
            "child_age_months": child_age_months,
            "risk_tier": "CRITICAL_AGE_OUT_CLIFF",
            "clinical_guidance": "Fast-track expedited evaluation: parallel Part B preschool notification required immediately.",
            "urgent_buffer_flag": True,
        }
    elif child_age_months >= 30:
        return {
            "child_age_months": child_age_months,
            "risk_tier": "ELEVATED_TRANSITION_RISK",
            "clinical_guidance": "Flag 60-day Part B transition conference upon initial IFSP scheduling.",
            "urgent_buffer_flag": True,
        }
    else:
        return {
            "child_age_months": child_age_months,
            "risk_tier": "STANDARD_UNDER_3",
            "clinical_guidance": "Standard Part C 45-day evaluation workflow.",
            "urgent_buffer_flag": False,
        }
