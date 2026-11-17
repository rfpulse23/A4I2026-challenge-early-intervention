-- scripts/02_create_transit_guardrails.sql
-- Zero-Vehicle Transit Accessibility Guardrail
-- Combines real US Census ACS 5-Year zero-vehicle household rates with geodesic
-- distance to the nearest bilingual Medicaid evaluation center.
-- Prerequisites:
--   1. acs_under5_tract_demographics loaded
--   2. pediatric_and_ei_provider_directory loaded

CREATE OR REPLACE TABLE `a4i_early_intervention.tract_transit_guardrails` AS
SELECT
    d.census_tract_geoid,
    d.county_name,
    d.state_code,
    ROUND(d.poverty_rate * 100, 1) AS poverty_pct,
    ROUND(d.no_vehicle_rate * 100, 1) AS no_vehicle_pct,
    p.provider_id AS nearest_eval_hub_id,
    p.synthetic_organization_name AS nearest_bilingual_eval_hub,
    ROUND(ST_DISTANCE(ST_CENTROID(d.tract_geom), p.provider_geom) / 1000.0, 1) AS distance_km,
    CASE 
        WHEN d.no_vehicle_rate >= 0.15 AND ST_DISTANCE(ST_CENTROID(d.tract_geom), p.provider_geom) > 5000 
            THEN 'HIGH_TRANSIT_BARRIER'
        WHEN d.no_vehicle_rate >= 0.15 
            THEN 'LOCAL_OR_WALKABLE'
        ELSE 'PERSONAL_VEHICLE_ASSUMED'
    END AS transit_risk_tier,
    IF(d.no_vehicle_rate >= 0.15 AND ST_DISTANCE(ST_CENTROID(d.tract_geom), p.provider_geom) > 5000,
       'Dispatch mobile evaluation van or schedule tele-intake',
       'Standard on-site clinic appointment') AS coordinator_action
FROM `a4i_early_intervention.acs_under5_tract_demographics` d
CROSS JOIN `a4i_early_intervention.pediatric_and_ei_provider_directory` p
WHERE p.node_role = 'Multidisciplinary_Eval_Hub'
  AND p.accepts_medicaid = TRUE
  AND p.bilingual_services_listed = TRUE
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY d.census_tract_geoid 
    ORDER BY ST_DISTANCE(ST_CENTROID(d.tract_geom), p.provider_geom) ASC
) = 1;
