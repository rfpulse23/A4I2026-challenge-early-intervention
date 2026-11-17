# Data Assumptions & Operational Model

This document outlines the clinical, legal, and statistical assumptions governing our data architecture, BigQuery queries, and graph triage pipelines.

---

## 1. Synthetic Privacy vs. Real Geographic Equity

* **Synthetic Boundaries:** To protect clinician identities and avoid attaching fictional waitlists or statutory non-compliance to real medical practices, **100% of providers (`CareNode`), lead agencies, and referral handoff logs (`ReferralHandoff`) are synthetic.**
* **Public Data Grounding:** Census tract boundaries (`tract_geom`), under-5 population counts, poverty rates, and zero-vehicle household percentages are **real public US Census Bureau American Community Survey (ACS) 5-Year estimates** anchored to standard FIPS geography.

---

## 2. Transit Accessibility & Spatial Guardrails

* **Physical Threshold:** Caregivers in census tracts where $\ge 15\%$ of households lack a personal vehicle cannot reasonably walk $> 5\text{ km}$ (~3.1 miles) with an infant or toddler to reach a clinic.
* **Operational Rationale:** Relying on third-party commercial transit routing or static GTFS bus schedules introduces severe license restrictions and fails completely in rural counties where scheduled municipal transit does not exist.
* **Action Trigger:** When a high-poverty, low-vehicle tract exceeds the 5 km threshold to the nearest Medicaid-accepting bilingual hub, the system automatically flags `HIGH_TRANSIT_BARRIER` and triggers recommendations for a Mobile Developmental Evaluation Team or Telehealth Intake.

---

## 3. Language Access & The ACS Trap

* **Data Finding:** In the starter ACS extract, `limited_english_rate` and `limited_english_speaking_pop_count` contain `0.0` across all tracts.
* **Decision:** We strictly avoid filtering or scoring on this column. 
* **Operational Solution:** Language access is enforced at the provider level by matching non-English-speaking referrals strictly to multidisciplinary evaluation hubs where `bilingual_services_listed = TRUE`.

---

## 4. Survey Grain & The Ecological Fallacy (HRSA NSCH)

* **Data Finding:** The HRSA National Survey of Children's Health (`nsch_developmental_screening_survey`) is modeled at the **Statewide level only** across six strata (four income bands and two primary home languages).
* **Grain Inoculation:** Joining NSCH to tract demographics on `state_code` alone multiplies every tract by 6x, artificially inflating population totals.
* **Operational Solution:** We treat NSCH strictly as statewide macro-context (e.g., establishing that non-English-speaking toddlers in Mississippi are screened at roughly half the rate of English-speaking toddlers). To prevent accidental 6x fan-out in ad-hoc queries, we provide `v_state_screening_benchmarks`, which pivots NSCH strata into a single row per state.

---

## 5. Post-Output Equity Auditing (Algorithmic Fairness)

* **Quarantine Rule:** Demographic race and ethnicity share columns (`audit_black_share`, `audit_hispanic_share`, etc.) are **strictly prohibited** from routing logic, priority scoring, or agent triage prompts.
* **Audit Methodology:** Demographics are joined strictly *post-output* to evaluate historical system performance—specifically auditing whether 3- to 4-hop paper-fax bottlenecks disproportionately accumulated in historically marginalized tracts.

---

## 6. Statutory 45-Day Clock (Calendar vs. Business Days)

* **Legal Context:** Under 34 CFR § 303.310 (IDEA Part C), the 45-day timeline from initial referral to completed Individualized Family Service Plan (IFSP) runs on **calendar days**, not business days.
* **Operational Implication:** Delays caused by transmission latency (such as paper faxes sitting unreviewed over weekends or clinic holidays) directly consume the family's statutory timeline.

---

## 7. 36-Month Age-Out Cliff & Part B Transition

* **Jurisdictional Boundary:** Federal Part C early intervention legally terminates on the child's third birthday (36 months), at which point jurisdiction transfers to local school district Part B preschool special education.
* **Clinical Triage:** Children entering referral at $\ge 30$ months are stratified into elevated and critical risk tiers, triggering expedited evaluation fast-tracking and concurrent 60-day Part B transition conferences to prevent service lapses.
