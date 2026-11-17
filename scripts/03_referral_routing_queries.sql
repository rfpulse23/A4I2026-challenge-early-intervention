-- scripts/03_referral_routing_queries.sql
-- Production ISO GQL and SQL queries for Early Intervention Triage:
-- 1. Multi-Hop Historical Breach Diagnosis (Exposing paper-fax bounce hubs)
-- 2. Prospective Compliant Pathway Discovery (<= 45-day IDEA Part C routes)
-- 3. Post-Output Equity Audit

-- ============================================================================
-- Query 1: Diagnose 3-4 Hop Breaches & Isolate Paper-Fax Bounce Hubs
-- Shows why flat waitlist sorting fails: Intake coordinators with low
-- internal wait times trigger 70+ day multi-hop breaches via paper fax.
-- ============================================================================
GRAPH `a4i_early_intervention.ReferralGraph`
MATCH (clinic:CareNode {node_role: 'Screening_Pediatric_Clinic'})
      -[hops:ReferralHandoff]->{2,4}
      (vendor:CareNode {node_role: 'EI_Therapy_Vendor'})
WHERE ARRAY_LENGTH(hops) >= 3
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
LIMIT 15;

-- ============================================================================
-- Query 2: Find Compliant <=45-Day Pathways for Incoming Referral
-- Matches child parameters: Medicaid eligibility, bilingual evaluation hub,
-- and cumulative wait time within the statutory 45-day ceiling.
-- ============================================================================
GRAPH `a4i_early_intervention.ReferralGraph`
MATCH (clinic:CareNode {node_role: 'Screening_Pediatric_Clinic'})
      -[h1:ReferralHandoff]-> (coord:CareNode {node_role: 'Part_C_Intake_Coordinator'})
      -[h2:ReferralHandoff]-> (eval:CareNode {node_role: 'Multidisciplinary_Eval_Hub'})
      -[h3:ReferralHandoff]-> (vendor:CareNode {node_role: 'EI_Therapy_Vendor'})
WHERE eval.accepts_medicaid = TRUE
  AND eval.bilingual_services_listed = TRUE
  AND vendor.vendor_enrolled_in_part_c = TRUE
  AND (h1.handoff_wait_days + h2.handoff_wait_days + h3.handoff_wait_days) <= 45
RETURN
  clinic.synthetic_organization_name AS clinic_name,
  coord.synthetic_organization_name AS coordinator_name,
  h1.transmission_channel AS clinic_to_coord_channel,
  eval.synthetic_organization_name AS eval_hub_name,
  h2.transmission_channel AS coord_to_eval_channel,
  vendor.synthetic_organization_name AS vendor_name,
  h3.transmission_channel AS eval_to_vendor_channel,
  (h1.handoff_wait_days + h2.handoff_wait_days + h3.handoff_wait_days) AS total_cumulative_wait_days
ORDER BY total_cumulative_wait_days ASC
LIMIT 10;

-- ============================================================================
-- Query 3: Post-Output Equity Audit
-- Audits whether historical >45-day breaches fell disproportionately on
-- high-poverty, zero-vehicle, and minority neighborhoods.
-- (Banned from routing rules; strictly evaluated post-output).
-- ============================================================================
WITH chain_totals AS (
    SELECT
        case_chain_id,
        ANY_VALUE(child_home_tract_geoid) AS child_home_tract_geoid,
        SUM(handoff_wait_days) AS episode_wait_days
    FROM `a4i_early_intervention.deidentified_part_c_referral_logs`
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
INNER JOIN `a4i_early_intervention.acs_under5_tract_demographics` AS d
    ON c.child_home_tract_geoid = d.census_tract_geoid
GROUP BY 1
ORDER BY 1;

-- ============================================================================
-- Query 4: Counterfactual Bottleneck Simulation
-- Models the operational impact of replacing paper fax handoffs at regional
-- intake hubs with electronic portal routing (4-day baseline wait).
-- Computes child-days recovered and reduction in federal 45-day statutory breaches.
-- ============================================================================
WITH simulation AS (
    SELECT
        case_chain_id,
        -- Actual baseline wait days for the referral episode
        SUM(handoff_wait_days) AS baseline_wait_days,
        -- Simulated wait days: replace paper_fax with electronic intake (4 days)
        SUM(IF(transmission_channel = 'paper_fax', 4, handoff_wait_days)) AS simulated_wait_days
    FROM `a4i_early_intervention.deidentified_part_c_referral_logs`
    GROUP BY case_chain_id
)
SELECT
    COUNT(*) AS total_episodes,
    COUNTIF(baseline_wait_days > 45) AS baseline_breaches,
    COUNTIF(simulated_wait_days <= 45 AND baseline_wait_days > 45) AS cases_recovered_to_compliance,
    ROUND(COUNTIF(simulated_wait_days <= 45 AND baseline_wait_days > 45) * 100.0 / COUNTIF(baseline_wait_days > 45), 1) AS recovery_rate_pct,
    SUM(baseline_wait_days - simulated_wait_days) AS total_child_days_saved
FROM simulation;

-- ============================================================================
-- Query 5: Part C Age-Out Risk Triage (36-Month Transition Cliff)
-- Part C eligibility terminates on the child's 3rd birthday (36 months).
-- Referrals arriving at 30+ months require fast-tracked evaluations and
-- concurrent Part B preschool notification to avoid service disruption.
-- ============================================================================
SELECT
    child_age_months,
    CASE 
        WHEN child_age_months >= 32 THEN 'CRITICAL_AGE_OUT_CLIFF'
        WHEN child_age_months >= 30 THEN 'ELEVATED_TRANSITION_RISK'
        ELSE 'STANDARD_UNDER_3'
    END AS transition_risk_tier,
    CASE 
        WHEN child_age_months >= 32 THEN 'Fast-track expedited evaluation: parallel Part B preschool notification required'
        WHEN child_age_months >= 30 THEN 'Flag 60-day Part B transition conference upon initial IFSP scheduling'
        ELSE 'Standard Part C 45-day evaluation workflow'
    END AS clinical_action_guidance
FROM UNNEST([18, 22, 28, 30, 32, 34]) AS child_age_months
ORDER BY child_age_months DESC;

-- ============================================================================
-- Query 6: Community Screening Season Outreach Prioritization (Track 3)
-- Prioritizes census tracts for mobile developmental screening team deployment
-- at community partner sites (Head Start, WIC centers, and family clinics).
-- Identifies high-poverty, transit-isolated tracts with high under-5 counts.
-- ============================================================================
SELECT
    d.census_tract_geoid,
    d.county_name,
    d.children_under_5_count,
    ROUND(d.poverty_rate * 100, 1) AS poverty_pct,
    ROUND(d.no_vehicle_rate * 100, 1) AS no_vehicle_pct,
    t.distance_km AS nearest_bilingual_hub_km,
    t.transit_risk_tier,
    CASE
        WHEN d.poverty_rate >= 0.30 AND d.no_vehicle_rate >= 0.15 
            THEN 'Priority 1: Mobile Screening Van at WIC / Head Start Hub'
        WHEN d.poverty_rate >= 0.20 
            THEN 'Priority 2: Community Developmental Screening Day'
        ELSE 'Priority 3: Standard Pediatric Practice Screening'
    END AS outreach_deployment_tier
FROM `a4i_early_intervention.acs_under5_tract_demographics` d
LEFT JOIN `a4i_early_intervention.tract_transit_guardrails` t
    ON d.census_tract_geoid = t.census_tract_geoid
ORDER BY d.poverty_rate DESC, d.no_vehicle_rate DESC
LIMIT 10;
