# Data Quality Log — PulseMetrics-Q

> Running audit of all anomalies identified and resolved across 9 tables.
> Updated after each notebook that performs cleaning.

---

## Notebook 02 — Data Quality Audit

| Table | Issue | Records Affected | Resolution |
|---|---|---|---|
| fact_admissions | Discharge before admission | 1,206 | Removed |
| fact_admissions | Duplicate rows | 594 | Removed |
| fact_admissions | Missing bed_id | ~3,600 | Filled with 'Unassigned' |
| fact_billing | Collected > Net amount (overbilling) | 2,400 | Flagged via overbilled_flag + excess_amount |
| fact_lab_orders | Report delivered before sample collected | 3,000 | Removed |
| fact_lab_orders | Missing tat_hours | ~4,000 | Imputed from timestamps |
| fact_pharmacy_orders | Invalid stockout flag (dispensed despite stockout) | 52 | Archived and removed |
| fact_pharmacy_orders | Incorrect total_cost | 1,748 | Recalculated |
| dim_patients | Negative age values | 111 | Removed |
| dim_patients | Duplicate patient records | 288 | Deduplicated (kept first) |
| dim_patients | Special character '@' in names | Multiple | Replaced with 'a' |
| dim_patients | Patient ID collision | 1 | Manually reassigned to P-060300 |

---

## Notebook 03 onwards — (to be updated)
