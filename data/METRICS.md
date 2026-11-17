# Challenge Metrics & Pitch Cheat Sheet (Mississippi Baseline)

This document provides verified baseline numbers, bottleneck statistics, and counterfactual simulation results for presentation slides, technical briefs, and video pitches.

---

## 1. Statutory 45-Day Compliance Overview

| Metric | Baseline Value | Clinical & Legal Significance |
|---|---|---|
| **Total Referral Episodes** | 44 episodes | State of Mississippi deidentified referral cohort. |
| **Multi-Hop Trajectories ($\ge 3$ hops)** | 35 episodes (79.5%) | Proves referrals are rarely 1-hop; they bounce through coordinators. |
| **Federal Statutory Breaches ($> 45$ days)** | **26 episodes (59.1%)** | Over half of children breach the IDEA Part C 45-calendar-day mandate. |
| **Mean Duration (Breached Episodes)** | **72.4 calendar days** | Nearly double the federal ceiling, delaying critical early therapy. |
| **Mean Duration (Compliant Episodes)** | 31.2 calendar days | Successfully resolved well under the 45-day statutory deadline. |

---

## 2. Root-Cause Bottleneck Diagnosis

* **The Primary Culprit:** Regional Intake Coordinator **`SYN-PROV-MS-012`**.
* **The Mechanism:** 
  * Intake Coordinator 012 relies predominantly on **`paper_fax`** transmissions.
  * While electronic portals process handoffs in ~4 days, `paper_fax` averages **~19.5 days per leg**.
  * When a child is bounced across 3 to 4 provider nodes through paper fax, transmission latency alone consumes 60–80 days before clinical evaluation even occurs.

---

## 3. Counterfactual Network Intervention (The "What-If" Fix)

**Simulation Parameter:** Upgrading `paper_fax` transmissions to standard electronic health record portal intake (`ehr_electronic_portal`, 4-day baseline wait).

| Counterfactual Metric | Result | Impact Statement |
|---|---|---|
| **Episodes Recovered to $\le 45$ Days** | **9 episodes** | 34.6% of all state breaches eliminated by a single channel upgrade. |
| **Coordinator 012 Episode Recovery** | **81.8% recovered** | Eliminates nearly all breaches passing through this intake hub. |
| **Cumulative Child-Days Saved** | **182 child-days** | 182 days of developmental delay therapy delivered earlier to toddlers. |

---

## 4. Transit Accessibility & Zero-Vehicle Equity

* **Total Census Tracts Evaluated:** 64 tracts in Mississippi.
* **Transit Desert Threshold:** Tracts where $\ge 15\%$ of households lack a personal vehicle AND geodesic distance to the nearest bilingual Medicaid evaluation hub $> 5\text{ km}$ (~3.1 miles).
* **Identified Hotspots:** Rural Delta tracts (e.g., Bolivar County tracts where distances to bilingual Medicaid evaluation centers exceed 20 km with zero municipal transit).
* **Automated Operational Directive:** Automatically flags `HIGH_TRANSIT_BARRIER` and triggers **Mobile Developmental Evaluation Team** dispatch or **Telehealth Intake**.

---

## 5. Developmental Screening & Language Access Disparities (HRSA NSCH)

* **English-Primary Household Screening Rate:** ~34%
* **Non-English Household Screening Rate:** ~18%
* **Equity Takeaway:** Non-English-speaking toddlers in Mississippi are screened for developmental delays at **roughly half the rate** of English-speaking toddlers.
* **Mitigation:** Quarantined from routing logic to prevent algorithmic bias; strictly matched to providers with `bilingual_services_listed = TRUE`.

---

## 6. Part C 36-Month Age-Out Triage Tiers

* **$\ge 32$ Months (`CRITICAL_AGE_OUT_CLIFF`):** Fast-track 14-day evaluation; trigger parallel school district Part B preschool notification.
* **$\ge 30$ Months (`ELEVATED_TRANSITION_RISK`):** Standard 45-day evaluation; automatically schedule 60-day Part B transition conference.
* **$< 30$ Months (`STANDARD_UNDER_3`):** Standard Part C 45-day evaluation workflow.
