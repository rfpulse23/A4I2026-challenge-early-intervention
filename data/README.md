# data/

Pre-staged GeoParquet starter tables covering six states (`MS`, `AL`, `GA`, `TX`, `CA`, and `NY`). When `A4I_SNAPSHOT_BUCKET` is unset, both [`notebooks/c_ei_01_load_explore.ipynb`](../notebooks/c_ei_01_load_explore.ipynb) and [`scripts/load.sh`](../scripts/load.sh) filter and load your chosen state directly from these five files into `a4i_early_intervention` inside your Google Cloud project.

**Read the `data_provenance` column in every table.** Every provider, agency, and referral row in this challenge is **100% synthetic** on purpose so made-up waitlists or federal 45-day statutory violations are never attached to real clinicians or real clinic addresses. Judges check that your pitch states this plainly.

## Files in this folder

### `acs_under5_tract_demographics.parquet` (426 rows across 6 states)

- **Provenance:** **Real public data.** US Census Bureau American Community Survey (ACS) 5-Year under-5 population counts, poverty rates, zero-vehicle household rates, TIGER/Line polygons (`tract_geom`), and five `audit_*` demographic share columns.
- **All-zero column trap:** `limited_english_rate` and `limited_english_speaking_pop_count` are `0.0` in this ACS extract. Do not filter or weight on that column without checking it first. Use `nsch_developmental_screening_survey.primary_home_language` and `pediatric_and_ei_provider_directory.bilingual_services_listed` for language-access analysis instead.
- **Equity Audit rule:** Never use `audit_*` columns inside routing rules. Join them after generating recommendations for your post-output Equity Audit.

### `nsch_developmental_screening_survey.parquet` (36 rows: 6 strata per state)

- **Provenance:** **Modeled state-level strata calibrated to public federal totals.** Calibrated to the HRSA National Survey of Children's Health (NSCH) NPM-6 developmental screening indicator. NSCH is published at the **state level only** (`geographic_level = 'Statewide'`), with zero county or census-tract coverage.
- **Grain trap:** Joining this table to census tracts on `state_code` alone duplicates every tract 6x (one per income/language stratum). Always filter to a specific stratum or aggregate intentionally.

### `idea_part_c_agency_performance.parquet` (18 rows: 3 synthetic regional agencies per state)

- **Provenance:** **100% `[Synthetic]` regional lead agencies.** Fictional regional IDEA Part C hubs (`SYN-PARTC-*`, `synthetic_agency_name`, `synthetic_office_address`) with timely 45-day IFSP performance metrics calibrated to US Department of Education Office of Special Education Programs (OSEP) Indicator C7 state reports.

### `pediatric_and_ei_provider_directory.parquet` (180 rows: 30 `CareNode` vertices per state)

- **Provenance:** **100% `[Synthetic]` organizational graph vertices.** Fictional clinics, intake coordinators, multidisciplinary evaluation hubs, and therapy vendors (`SYN-PROV-*`, `synthetic_organization_name`, `synthetic_address`) anchored to real US Census tracts. Zero real NPPES clinicians or real street addresses appear here.
- **Graph DDL note:** Exclude `provider_geom` (`PROPERTIES ALL COLUMNS EXCEPT (provider_geom)`) when declaring your BigQuery Property Graph so all vertex properties remain scalar GQL types (`latitude` and `longitude` remain on `CareNode`).

### `deidentified_part_c_referral_logs.parquet` (894 rows: 149 directed `ReferralHandoff` edges across 44 chains per state)

- **Provenance:** **100% `[Synthetic]` multi-hop referral and re-referral bounce logs.** Variable-length (`2` to `4` hop) referral chains (`case_chain_id`, `hop_sequence`, `transmission_channel`, `handoff_wait_days`) inside the same `a4i_early_intervention` dataset, designed so ISO GQL variable-length path queries (`-{2,4}->`) uncover multi-hop paper-fax bounce loops breaching the federal 45-day IDEA Part C clock.

### `tract_transit_guardrails` (Derived in BigQuery)

- **Provenance:** Derived table combining real US Census ACS 5-Year zero-vehicle household rates (`acs_under5_tract_demographics`) with geodesic distance to the nearest bilingual Medicaid evaluation center (`pediatric_and_ei_provider_directory`).
- **Purpose:** Identifies transit deserts where families lack personal vehicles and live >5 km from an evaluation hub.
- **Action Trigger:** Automatically flags `HIGH_TRANSIT_BARRIER` and triggers recommendations for mobile developmental evaluation vans or tele-intake.
- **State Scope:** Pre-computed for Mississippi (`MS`); dynamically reproducible for `AL`, `GA`, `TX`, `CA`, and `NY`.
