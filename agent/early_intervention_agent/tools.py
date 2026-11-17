import os
from google.cloud import bigquery

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-5956a6cfcbdf")
DATASET = "a4i_early_intervention"
TARGET_STATE = os.environ.get("TARGET_STATE", "MS")
bq_client = bigquery.Client(project=PROJECT_ID)


def trace_breached_referral_chains(min_hops: int = 3, max_hops: int = 4) -> str:
    """Traces variable-length multi-hop referral chains (2 to 4 hops) in BigQuery ReferralGraph
    for Mississippi (MS) that breached the 45-day IDEA Part C federal limit.
    Correlates case_chain_id across hops to expose hidden bounce hubs and paper_fax delays.
    """
    query = f"""
    GRAPH `{PROJECT_ID}.{DATASET}.ReferralGraph`
    MATCH (clinic:CareNode {{node_role: 'Screening_Pediatric_Clinic'}})
          -[hops:ReferralHandoff]->{{{min_hops},{max_hops}}}
          (vendor:CareNode {{node_role: 'EI_Therapy_Vendor'}})
    WHERE clinic.state_code = @state_code
      AND ARRAY_LENGTH(hops) >= {min_hops}
      AND (SELECT COUNT(DISTINCT h.case_chain_id) FROM UNNEST(hops) AS h) = 1
    LET total_hops = ARRAY_LENGTH(hops),
        chain_id = hops[OFFSET(0)].case_chain_id,
        chain_wait_days = (SELECT SUM(h.handoff_wait_days) FROM UNNEST(hops) AS h),
        fax_hops = (SELECT COUNTIF(h.transmission_channel = 'paper_fax') FROM UNNEST(hops) AS h)
    FILTER chain_wait_days > 45
    RETURN
      chain_id,
      clinic.provider_id AS origin_clinic_id,
      clinic.synthetic_organization_name AS origin_clinic,
      hops[OFFSET(0)].target_provider_id AS intake_coordinator_id,
      vendor.provider_id AS final_vendor_id,
      vendor.synthetic_organization_name AS final_vendor,
      total_hops,
      fax_hops,
      chain_wait_days,
      ARRAY(
        SELECT CONCAT(
          h.source_provider_id, ' --[',
          CAST(h.handoff_wait_days AS STRING), 'd, ',
          h.transmission_channel, ']--> ',
          h.target_provider_id
        )
        FROM UNNEST(hops) AS h
      ) AS hop_trace
    ORDER BY chain_wait_days DESC
    LIMIT 15
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("state_code", "STRING", TARGET_STATE)]
    )
    rows = [dict(row) for row in bq_client.query(query, job_config=job_config).result()]
    return str(rows)


def find_compliant_pathway(
    origin_tract_geoid: str = "",
    requires_medicaid: bool = True,
    requires_bilingual: bool = True,
    max_days: int = 45,
) -> str:
    """Finds valid <=45-day multi-hop pathways in Mississippi (MS) from Screening_Pediatric_Clinic
    to EI_Therapy_Vendor, enforcing Medicaid acceptance, bilingual services, Part C vendor enrollment,
    correlated case_chain_id, and spatial distance (ST_DISTANCE in km) from the child's home census tract.
    """
    query = f"""
    WITH graph_paths AS (
      SELECT *
      FROM GRAPH_TABLE(
        `{PROJECT_ID}.{DATASET}.ReferralGraph`
        MATCH (clinic:CareNode {{node_role: 'Screening_Pediatric_Clinic'}})
              -[hops:ReferralHandoff]->{{2,4}}
              (vendor:CareNode {{node_role: 'EI_Therapy_Vendor'}})
        WHERE clinic.state_code = @state_code
          AND (SELECT COUNT(DISTINCT h.case_chain_id) FROM UNNEST(hops) AS h) = 1
          AND (@requires_medicaid = FALSE OR vendor.accepts_medicaid = TRUE)
          AND (@requires_bilingual = FALSE OR vendor.bilingual_services_listed = TRUE)
          AND vendor.part_c_vendor_enrolled = TRUE
        LET chain_id = hops[OFFSET(0)].case_chain_id,
            total_hops = ARRAY_LENGTH(hops),
            chain_wait_days = (SELECT SUM(h.handoff_wait_days) FROM UNNEST(hops) AS h)
        FILTER chain_wait_days <= @max_days
        RETURN
          chain_id,
          clinic.provider_id AS clinic_id,
          clinic.synthetic_organization_name AS origin_clinic,
          vendor.provider_id AS vendor_id,
          vendor.synthetic_organization_name AS final_vendor,
          vendor.accepts_medicaid AS accepts_medicaid,
          vendor.bilingual_services_listed AS bilingual_services_listed,
          total_hops,
          chain_wait_days,
          ARRAY(
            SELECT CONCAT(
              h.source_provider_id, ' --[',
              CAST(h.handoff_wait_days AS STRING), 'd, ',
              h.transmission_channel, ']--> ',
              h.target_provider_id
            )
            FROM UNNEST(hops) AS h
          ) AS route_steps
      )
    ),
    tract_info AS (
      SELECT
        census_tract_geoid,
        no_vehicle_rate,
        poverty_rate,
        ST_CENTROID(tract_geom) AS tract_center
      FROM `{PROJECT_ID}.{DATASET}.acs_under5_tract_demographics`
      WHERE state_code = @state_code
        AND (@origin_tract_geoid = '' OR census_tract_geoid = @origin_tract_geoid)
      LIMIT 1
    )
    SELECT
      g.*,
      t.census_tract_geoid AS evaluated_tract_geoid,
      ROUND(t.no_vehicle_rate, 3) AS tract_no_vehicle_rate,
      ROUND(t.poverty_rate, 3) AS tract_poverty_rate,
      ROUND(ST_DISTANCE(p.provider_geom, t.tract_center) / 1000.0, 1) AS distance_to_vendor_km
    FROM graph_paths g
    JOIN `{PROJECT_ID}.{DATASET}.pediatric_and_ei_provider_directory` p
      ON g.vendor_id = p.provider_id
    LEFT JOIN tract_info t
      ON TRUE
    ORDER BY g.chain_wait_days ASC, distance_to_vendor_km ASC
    LIMIT 10
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("state_code", "STRING", TARGET_STATE),
            bigquery.ScalarQueryParameter("origin_tract_geoid", "STRING", str(origin_tract_geoid)),
            bigquery.ScalarQueryParameter("requires_medicaid", "BOOL", requires_medicaid),
            bigquery.ScalarQueryParameter("requires_bilingual", "BOOL", requires_bilingual),
            bigquery.ScalarQueryParameter("max_days", "INT64", max_days),
        ]
    )
    rows = [dict(row) for row in bq_client.query(query, job_config=job_config).result()]
    return str(rows)


def simulate_fax_upgrade_counterfactual(coordinator_id: str = "", new_wait_days_per_fax_hop: int = 2) -> str:
    """Identifies the top regional bounce hub in Mississippi (MS) and simulates upgrading its paper_fax
    handoffs to electronic e-referral, quantifying exact breached episodes resolved and child-days saved.
    """
    query = f"""
    WITH hub_stats AS (
      SELECT
        source_provider_id AS hub_id,
        COUNT(DISTINCT case_chain_id) AS chains_touched,
        COUNTIF(transmission_channel = 'paper_fax') AS fax_handoffs,
        SUM(CASE WHEN transmission_channel = 'paper_fax' THEN handoff_wait_days ELSE 0 END) AS fax_wait_days
      FROM `{PROJECT_ID}.{DATASET}.deidentified_part_c_referral_logs`
      WHERE state_code = @state_code
      GROUP BY source_provider_id
      ORDER BY fax_wait_days DESC
    ),
    target AS (
      SELECT COALESCE(NULLIF(@coordinator_id, ''), (SELECT hub_id FROM hub_stats LIMIT 1)) AS chosen_hub_id
    ),
    chain_sim AS (
      SELECT
        l.case_chain_id,
        SUM(l.handoff_wait_days) AS original_days,
        SUM(
          CASE
            WHEN l.source_provider_id = t.chosen_hub_id AND l.transmission_channel = 'paper_fax'
            THEN @new_wait_days_per_fax_hop
            ELSE l.handoff_wait_days
          END
        ) AS simulated_days
      FROM `{PROJECT_ID}.{DATASET}.deidentified_part_c_referral_logs` l
      CROSS JOIN target t
      WHERE l.state_code = @state_code
      GROUP BY l.case_chain_id
      HAVING MAX(CASE WHEN l.source_provider_id = t.chosen_hub_id OR l.target_provider_id = t.chosen_hub_id THEN 1 ELSE 0 END) = 1
    )
    SELECT
      (SELECT chosen_hub_id FROM target) AS target_bounce_hub_id,
      p.synthetic_organization_name AS target_bounce_hub_name,
      p.median_internal_wait_days AS flat_spreadsheet_internal_wait_days,
      COUNT(*) AS total_chains_through_hub,
      COUNTIF(c.original_days > 45) AS breached_45d_before_fix,
      COUNTIF(c.simulated_days > 45) AS breached_45d_after_fix,
      SUM(c.original_days - c.simulated_days) AS total_child_days_saved
    FROM chain_sim c
    JOIN `{PROJECT_ID}.{DATASET}.pediatric_and_ei_provider_directory` p
      ON p.provider_id = (SELECT chosen_hub_id FROM target)
    GROUP BY target_bounce_hub_name, flat_spreadsheet_internal_wait_days
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("state_code", "STRING", TARGET_STATE),
            bigquery.ScalarQueryParameter("coordinator_id", "STRING", coordinator_id),
            bigquery.ScalarQueryParameter("new_wait_days_per_fax_hop", "INT64", new_wait_days_per_fax_hop),
        ]
    )
    rows = [dict(row) for row in bq_client.query(query, job_config=job_config).result()]
    return str(rows)


def run_post_output_equity_audit() -> str:
    """Runs the post-output Equity Audit for Mississippi (MS), joining referral chain outcomes to
    acs_under5_tract_demographics (audit_* shares, poverty_rate, no_vehicle_rate) and statewide NSCH benchmarks.
    Strictly excluded from routing decisions and used only to audit disparate impact.
    """
    query = f"""
    WITH chain_totals AS (
      SELECT
        case_chain_id,
        ANY_VALUE(child_home_tract_geoid) AS child_home_tract_geoid,
        SUM(handoff_wait_days) AS total_days,
        COUNT(*) AS hop_count
      FROM `{PROJECT_ID}.{DATASET}.deidentified_part_c_referral_logs`
      WHERE state_code = @state_code
      GROUP BY case_chain_id
    )
    SELECT
      c.total_days > 45 AS breached_45_days,
      COUNT(*) AS episode_count,
      ROUND(AVG(c.total_days), 1) AS avg_total_days,
      ROUND(AVG(d.poverty_rate), 3) AS avg_poverty_rate,
      ROUND(AVG(d.no_vehicle_rate), 3) AS avg_no_vehicle_rate,
      ROUND(AVG(d.audit_black_share), 3) AS avg_audit_black_share,
      ROUND(AVG(d.audit_hispanic_share), 3) AS avg_audit_hispanic_share,
      ROUND(AVG(d.audit_white_share), 3) AS avg_audit_white_share
    FROM chain_totals c
    JOIN `{PROJECT_ID}.{DATASET}.acs_under5_tract_demographics` d
      ON c.child_home_tract_geoid = d.census_tract_geoid
    GROUP BY breached_45_days
    ORDER BY breached_45_days DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("state_code", "STRING", TARGET_STATE)]
    )
    rows = [dict(row) for row in bq_client.query(query, job_config=job_config).result()]
    return str(rows)
