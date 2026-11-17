-- scripts/01_create_property_graph.sql
-- Declares the BigQuery Property Graph for Early Intervention multi-hop triage.
-- Prerequisites:
--   1. Tables loaded into a4i_early_intervention (run scripts/load.sh <STATE>)
--   2. Enterprise reservation active (a4i-graph)

CREATE OR REPLACE PROPERTY GRAPH `a4i_early_intervention.ReferralGraph`
  NODE TABLES (
    `a4i_early_intervention.pediatric_and_ei_provider_directory` AS CareNode
      KEY (provider_id)
      LABEL CareNode
      PROPERTIES ALL COLUMNS EXCEPT (provider_geom)
  )
  EDGE TABLES (
    `a4i_early_intervention.deidentified_part_c_referral_logs` AS ReferralHandoff
      KEY (referral_event_id)
      SOURCE KEY (source_provider_id) REFERENCES CareNode (provider_id)
      DESTINATION KEY (target_provider_id) REFERENCES CareNode (provider_id)
      LABEL ReferralHandoff
      PROPERTIES ALL COLUMNS
  );
