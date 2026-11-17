-- scripts/04_state_screening_view.sql
-- Inoculation against the 6x NSCH Grain Trap.
-- Collapses multi-strata statewide HRSA NSCH screening rates into a single row
-- per state, pivoting English vs. Non-English and poverty benchmarks.
-- Joining this view against tract demographics on state_code yields zero row duplication.

CREATE OR REPLACE VIEW `a4i_early_intervention.v_state_screening_benchmarks` AS
SELECT
    state_code,
    MAX(IF(primary_home_language = 'English', standardized_screening_rate_pct, NULL)) AS screening_pct_english_homes,
    MAX(IF(primary_home_language = 'Non-English', standardized_screening_rate_pct, NULL)) AS screening_pct_non_english_homes,
    MAX(IF(household_income_fpl_band = '<100% FPL', standardized_screening_rate_pct, NULL)) AS screening_pct_poverty_homes,
    MAX(IF(primary_home_language = 'Non-English', followup_requested_pct, NULL)) AS followup_requested_pct_non_english,
    MAX(IF(primary_home_language = 'English', followup_requested_pct, NULL)) AS followup_requested_pct_english
FROM `a4i_early_intervention.nsch_developmental_screening_survey`
GROUP BY state_code;
