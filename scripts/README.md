# scripts/

Headless alternatives to the notebook, for when a Colab Enterprise runtime is slow or
unavailable.

`load.sh` reaches the same end state as `notebooks/c_ei_01_load_explore.ipynb`—provisioning the
zero-baseline Enterprise reservation (`a4i-graph`, \$0 when idle) required for BigQuery Graph
(`GQL`) and rebuilding all five BigQuery tables in `a4i_early_intervention` with native `GEOGRAPHY`
columns (`tract_geom`, `intake_geom`, `provider_geom`) and leading-zero-safe 11-digit tract GEOIDs.
Use the notebook if you can: Section 2 proves why sorting flat provider waitlists misses multi-hop
`paper_fax` coordinator bottlenecks, and Sections 4–5 expose the all-zero `limited_english_rate`
column and 6× statewide NSCH grain traps. Use this script if you cannot.

## Running it

From the **root of the repo**, in Cloud Shell:

```bash
bash scripts/load.sh              # loads Mississippi (MS)—the default
bash scripts/load.sh AL           # Alabama (leading-zero FIPS 01)
bash scripts/load.sh CA           # California (leading-zero FIPS 06)
bash scripts/load.sh --list       # show every pre-staged state
bash scripts/load.sh --help       # usage
```

**It takes a two-letter state abbreviation (`MS`, `AL`, `GA`, `TX`, `CA`, `NY`).** Invoke it with
`bash` rather than `./scripts/load.sh` so it works regardless of whether the file's executable bit
survived how your copy of the repository was created.

If `A4I_SNAPSHOT_BUCKET` is configured in `.env` (or exported in your shell; see `.env.example`),
`load.sh` loads pre-filtered GeoParquet snapshots from Cloud Storage. Otherwise, it loads and
filters directly from the repository's `data/*.parquet` files using `bq`.

## It is safe to run more than once

Both the `a4i-graph` Enterprise reservation setup and every `--replace` table load are idempotent.
Canceling halfway through or switching states on a second run overwrites the previous state's
tables cleanly without mixing states.

## What the verification block checks

- **Enterprise graph reservation (`a4i-graph`)**: `ENTERPRISE`, `0` baseline slots, `50` autoscale
  max slots, assigned to `QUERY` jobs in your project (`US`).
- **Multi-hop graph topology & 45-day statutory breaches**: verifies `>= 2`-hop referral chains,
  `> 45`-day IDEA Part C episode breaches, and `0` orphan `source_provider_id` /
  `target_provider_id` foreign keys against `pediatric_and_ei_provider_directory`.

---

## Production SQL & Graph Query Catalog

In addition to `load.sh`, this directory provides production-ready SQL and ISO GQL scripts ready to execute in BigQuery Studio or via the BigQuery Python SDK:

| Script | Type | Target / Output | Purpose |
|---|---|---|---|
| [`01_create_property_graph.sql`](01_create_property_graph.sql) | DDL (ISO GQL) | `a4i_early_intervention.ReferralGraph` | Declares property graph with `CareNode` vertices and `ReferralHandoff` edges across 4 provider roles. |
| [`02_create_transit_guardrails.sql`](02_create_transit_guardrails.sql) | DDL / Spatial SQL | `a4i_early_intervention.tract_transit_guardrails` | Joins Census ACS zero-vehicle rates with `ST_DISTANCE` to nearest bilingual Medicaid hub. |
| [`03_referral_routing_queries.sql`](03_referral_routing_queries.sql) | Query Suite | Queries 1–6 | Production queries covering: Multi-hop breach diagnosis (`-{2,4}->`), compliant pathway discovery, post-output equity audit, counterfactual transmission upgrade simulation, 36-month age-out cliff triage, and Track 3 community screening outreach. |
| [`04_state_screening_view.sql`](04_state_screening_view.sql) | DDL (View) | `a4i_early_intervention.v_state_screening_benchmarks` | Pivots HRSA NSCH survey strata into 1 row per state to prevent the 6x Cartesian join fan-out trap. |
