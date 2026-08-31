# 🏥 PulseMetrics-Q — EDA Roadmap & KPI Playbook (v2)

*Updated after completing data cleaning, master-table construction, and initial profiling. This version reflects the actual state of your `admission_master` table and the domain decisions you've made.*

---

## How to use this playbook

You've completed loading, cleaning, and building the `admission_master` table (118,800 rows × 86 columns). This document is the blueprint for the **remaining EDA work** in your notebook.

1. **What features should I engineer?** → Section 1 (temporal, demographic, clinical, financial, experience features).
2. **What KPIs should I create, and for what analysis?** → Sections 2–7 (a catalog by business domain).
3. **What calculations, cuts, and visualizations tie it together?** → Sections 8–10 (hierarchy, methodology, portfolio storylines).

Work top-to-bottom. Engineer features first (Section 1), then move through the domain sections.

---

## What's already done (for reference)

### ✅ Completed in your notebook (Cells 0–148)

| Step | Status | Detail |
|------|--------|--------|
| Load & profile all 9 CSVs | ✅ Done | `HospitalData` class, `.info()`, `.describe()` |
| Clean `dim_patients` | ✅ Done | Removed −1 ages, fixed `@` in names, deduplicated, reassigned `P-060300` |
| Clean `fact_admissions` | ✅ Done | Dropped 1,206 inverted-date rows, removed 594 duplicates, filled `bed_id` with `'Unassigned'` |
| Clean `fact_billing` | ✅ Done | Created `overbilled_flag` & `excess_amount`, fixed `outstanding_amount` (set to 0 when overpaid), filled `insurance_company`/`tpa_name` with `'NA'` |
| Clean `fact_lab_orders` | ✅ Done | Removed 3,000 invalid date sequences, imputed 4,000 missing `tat_hours` from timestamps |
| Clean `fact_patient_feedback` | ✅ Done | Clipped NPS to −100…100, computed `overall_csat` |
| Clean `fact_pharmacy_orders` | ✅ Done | Archived 52 invalid stockout records, recalculated `total_cost` |
| Orphan cleanup | ✅ Done | Synchronized all child tables to valid `admission_id` set |
| Export cleaned tables to `clean_data/` | ✅ Done | All 9 tables saved |
| Pre-aggregate to admission grain | ✅ Done | `lab_by_adm`, `rx_by_adm`, `fb_by_adm` |
| Build `admission_master` | ✅ Done | 118,800 rows × 86 columns, left-join strategy, zero fan-out |
| Drop redundant columns | ✅ Done | Removed `hospital_id_doc`, `hospital_id_bill`, `hospital_id_fdback`, `doctor_id_fdback`, `department_doc` |
| Rename for clarity | ✅ Done | `city` → `hospital_city`, `state` → `hospital_state` |
| Fill missing categoricals | ✅ Done | Patient demographics → `'Unspecified'`, accreditation → `'Unaccredited'`, complaint_category → conditional fill |
| `has_feedback` flag | ✅ Done | Boolean flag for feedback coverage |

### ✅ Coverage report (your denominators)

| Anchor | Coverage | Notes |
|--------|----------|-------|
| Admissions with Lab Tests | 95,682 / 118,800 (80.5%) | ~19.5% of admissions had no lab orders |
| Admissions with Pharmacy Orders | 92,212 / 118,800 (77.6%) | ~22.4% had no pharmacy dispensing |
| Admissions with Feedback Surveys | 39,577 / 118,800 (33.3%) | Voluntary survey — always state this denominator |
| Admissions with Billing | 118,800 / 118,800 (100%) | 1:1 relationship confirmed |
| Patient demographics available | 118,042 / 118,800 (99.4%) | 758 admissions link to removed patients |

---

## Reliability legend

| Flag | Meaning | What to do |
|------|---------|------------|
| 🟢 | **Trustworthy** — validated, safe to headline | Analyze freely |
| 🟡 | **Use with caution** — a residual quirk or construction artifact affects it | Apply the noted caveat |
| 🔴 | **Noise / broken** — the field does not mean what its name says | Do **not** present as a meaningful metric |

### 🔴 Fields that are noise — do not analyze as meaningful

| Field | Why it's unusable | Use instead |
|-------|-------------------|-------------|
| `payment_status` | All four statuses show identical ~0.806 collection ratio — uncorrelated with money columns | Derive collection status from `outstanding_amount` / `collected_amount` |
| `insurance_company`, `tpa_name` | Randomly assigned; 31,348 Self-Pay bills carry an insurer name | Don't infer payer behaviour from these |
| `payer_type` vs `insurance_type` | Disagree on ~77% of rows | Pick **one** as your payer lens (recommend `insurance_type`), state it, and don't cross-validate |
| `bed_id` | Only ~650 IDs reused across 25 hospitals; overlapping stays; plus `'Unassigned'` | Use **LOS-based** occupancy proxy (Section 4) |
| `registration_date` | 33% of patients "registered" *after* their first admission | Do **not** compute tenure, cohort, or acquisition-date analysis |
| `fiscal_year` | Labelled `FY2024-25` for every row while `quarter` follows the calendar | Ignore it; engineer your own fiscal quarter from `admission_date` |

### 🟡 Residual quirks — know before analyzing

| Field | Issue | How to handle |
|-------|-------|---------------|
| `collected_amount` on overbilled rows | ~2,400 rows where collected > net. `outstanding_amount` is now correctly set to 0, and `excess_amount` captures the overpayment | Use `overbilled_flag` to **exclude/segment** from collection-rate KPIs |
| `nps_score` | Per-response value (−100 to 100), not true group-level NPS | Aggregate as a **mean**, label it as a "proxy NPS" |

### ✅ Domain decisions you've made (with reasoning)

These were deliberate analytical choices — document them in your notebook so readers understand your rationale:

| Item | Your Decision | Reasoning |
|------|---------------|-----------|
| **Ages 0, 115, 130** | ✅ Keep as valid data | Age 0 = neonates/infants (valid in hospitals with Maternity/Paediatrics). Ages 115/130 = supercentenarians — will naturally fall into the `61+` or `80+` age band, preventing any skew on averages |
| **Rating scale 1–6** | ✅ Keep as a 6-point scale | Interpreted as [Extremely Bad, Bad, Not Bad, Neutral, Good, Excellent] — a valid 6-point Likert scale. State in notebook: *"Ratings evaluated on a 1–6 Likert scale"* |
| **Pharmacy: dispensed > ordered** | ✅ Keep as valid operational data | Five real-world clinical reasons: (1) Split dispensing across visits, (2) Pack-size rounding for liquids/inhalers, (3) Emergency/override dispensing, (4) Therapeutic substitution with different dosage form, (5) Auto-refill/standing orders. Present as a **"Clinical Audit: Over-Dispense & Protocol Overrides"** callout in the pharmacy section |

### 🟢 Confirmed trustworthy — headline freely

`length_of_stay` · billing arithmetic (`gross − discount = net`; four charge components sum to gross) · `tat_hours` & `tat_breach_flag` · all categorical text · `region`, `state`, `city`, `tier`, `accreditation`, `bed_capacity` · `specialization`, `experience_years`, `consultation_fee`, `employment_type` · `admission_type`, `ward_type`, `department` (on the admission row), `discharge_type` · ICD `category`/`severity_level`/`is_chronic` · `test_category`, `drug_category` · `gender`, `blood_group`.

---

## ⚠️ Temporal constraint — single-year data (Jan–Dec 2024)

Your `admission_date` spans **Jan 1, 2024 → Dec 30, 2024** (exactly 1 calendar year). This means:

| ❌ Cannot Do | ✅ Can Do |
|---|---|
| Year-over-Year (YoY) growth comparison | Monthly trends (12 data points) |
| Multi-year cohort analysis | Quarterly comparison (Q1 vs Q2 vs Q3 vs Q4) |
| Long-term seasonality validation | Single-year seasonal patterns (Winter / Summer / Monsoon / Post-Monsoon) |
| | Day-of-week analysis (weekday vs weekend) |
| | LOS, billing lag, and feedback lag distributions |

---

## Section 1 — Feature engineering catalog *(do this next)*

Build these on `admission_master`. Grouped by theme so you can knock them out in batches.

### A. Temporal features (from `admission_date`)

| Feature | Derivation | Enables | Flag |
|---------|-----------|---------|------|
| `adm_year` | `admission_date.dt.year` | grouping (even though single year) | 🟢 |
| `adm_month` | `admission_date.dt.month` | monthly trend, sorting | 🟢 |
| `adm_month_name` | `admission_date.dt.strftime('%b')` | display labels (Jan, Feb…) | 🟢 |
| `adm_quarter` | `admission_date.dt.quarter` | quarterly reporting (use this, **not** `fiscal_year` 🔴) | 🟢 |
| `adm_day_of_week` | `admission_date.dt.day_name()` | weekday vs weekend load | 🟢 |
| `adm_week_type` | `'Weekday'` if Mon–Fri, else `'Weekend'` | weekday/weekend comparison | 🟢 |
| `season` | Month mapped → Winter (Dec–Feb) / Summer (Mar–May) / Monsoon (Jun–Sep) / Post-Monsoon (Oct–Nov) | Indian seasonal disease patterns | 🟢 |
| `billing_lag_days` | `billing_date − admission_date` in days | billing efficiency / revenue-recognition delay | 🟢 |

### B. Patient / demographic features

| Feature | Derivation | Enables | Flag |
|---------|-----------|---------|------|
| `age_band` | Bins: 0–12 Paediatric, 13–18 Adolescent, 19–40 Young Adult, 41–60 Middle Age, 61+ Senior | demographic mix, disease-by-age | 🟢 |
| `is_senior` | `age >= 61` | high-risk cohort flag | 🟢 |
| `is_paediatric` | `age <= 12` | paediatric cohort flag | 🟢 |
| `patient_type` | As-is (New/Repeat) | acquisition vs retention | 🟢 |

### C. Clinical / operational features

| Feature | Derivation | Enables | Flag |
|---------|-----------|---------|------|
| `los_band` | `length_of_stay` → 1–3 Short, 4–7 Medium, 8–14 Long, 15+ Extended | LOS distribution, outlier stays | 🟢 |
| `is_long_stay` | `length_of_stay > 14` (or use p90) | efficiency flag | 🟢 |
| `is_emergency` | `admission_type == 'Emergency'` | acuity mix | 🟢 |
| `is_icu` | `ward_type == 'ICU'` | critical-care load | 🟢 |
| `mortality_flag` | `discharge_type == 'Expired'` | mortality rate | 🟢 |
| `adverse_discharge` | `discharge_type in ('Expired', 'LAMA')` | quality-of-care signal | 🟢 |
| `is_chronic` | Already in master from ICD join | chronic-disease burden | 🟢 |

### D. Financial features (per admission)

| Feature | Derivation | Enables | Flag |
|---------|-----------|---------|------|
| `collection_rate` | `collected_amount / net_amount` | revenue realization | 🟡 (exclude `overbilled_flag == 1`) |
| `outstanding_ratio` | `outstanding_amount / net_amount` | AR / bad-debt exposure | 🟡 (same caveat) |
| `discount_rate` | `discount_amount / gross_amount` | discount leakage | 🟢 |
| `revenue_per_bed_day` | `net_amount / length_of_stay` | ARPOB proxy — core hospital KPI | 🟢 |
| `procedure_pct` | `procedure_charges / gross_amount` | service-line revenue mix | 🟢 |
| `pharmacy_pct` | `pharmacy_charges / gross_amount` | service-line revenue mix | 🟢 |
| `lab_pct` | `lab_charges / gross_amount` | service-line revenue mix | 🟢 |
| `room_pct` | `room_charges / gross_amount` | service-line revenue mix | 🟢 |
| `is_high_value` | `net_amount >= p90` | high-value case profiling | 🟢 |
| `total_ancillary_cost` | `lab_total_cost + rx_total_cost` | ancillary spend per admission | 🟢 |
| `pharmacy_margin` | `pharmacy_charges − rx_total_cost` | pharmacy profitability proxy | 🟡 |

### E. Experience features (from feedback columns)

| Feature | Derivation | Enables | Flag |
|---------|-----------|---------|------|
| `csat_band` | Low ≤ 2.5 / Mid 2.5–4 / High ≥ 4 | satisfaction segmentation | 🟢 |
| `has_feedback` | ✅ Already created | coverage / response rate | 🟢 |
| `complaint_category` | ✅ Already cleaned (conditional fill) | complaint mix | 🟢 |

### F. Cross-table / interaction features

| Feature | Derivation | Enables | Flag |
|---------|-----------|---------|------|
| `tests_per_stay_day` | `test_count / length_of_stay` | diagnostic intensity | 🟢 |
| `has_critical_lab` | `critical_count > 0` | critical-result flag | 🟢 |

### 1.1 Reusable aggregation grains

Most KPIs are the same measures rolled to different grouping levels. These are your primary `groupby` dimensions:

`hospital_id` (+ `hospital_name` / `region` / `hospital_state` / `hospital_city` / `tier` / `accreditation`) · `department` · `specialization` · `doctor_id` · ICD `category` / `severity_level` / `is_chronic` · `admission_type` · `ward_type` · `insurance_type` (chosen payer lens) · `age_band` · `gender` · `patient_type` · `season` / `adm_month` / `adm_quarter`.

---

## Section 2 — Executive scorecard *(the chain-level "one-glance" KPIs)*

Start EDA with the top line: a dozen numbers a CEO would want, each with a trend and a branch ranking.

| KPI | Formula | Cuts to show | Flag | Best visual |
|-----|---------|--------------|------|-------------|
| Total admissions | `count(admission_id)` | overall, by month, by branch | 🟢 | KPI card + monthly line |
| Unique patients | `nunique(patient_id)` | overall | 🟢 | KPI card |
| Total net revenue | `sum(net_amount)` | by branch, quarter | 🟢 | KPI card + bar |
| Revenue per admission (ARPP) | `sum(net_amount) / count(admission_id)` | by branch, department | 🟢 | bar |
| Overall collection rate | `sum(collected_amount) / sum(net_amount)` **excluding `overbilled_flag==1`** | by branch, payer | 🟡 | gauge / bar |
| Accounts receivable (AR) | `sum(outstanding_amount)` **excluding overbilled rows** | by branch | 🟡 | KPI card |
| Average length of stay (ALOS) | `mean(length_of_stay)` | by department, severity | 🟢 | KPI card + box |
| Bed occupancy rate (proxy) | `sum(length_of_stay) / (sum(bed_capacity) × 365)` | by branch | 🟡 (LOS-based, **not** `bed_id`) | bar vs 100% |
| 30-day readmission rate | `mean(readmission_flag)` | by department, diagnosis | 🟢 | KPI card + bar |
| Mortality rate | `mean(discharge_type=='Expired')` | by severity, department | 🟢 | bar |
| Overall CSAT | `mean(overall_csat)` *on 1–6 Likert scale* | by branch | 🟡 (33% coverage) | gauge |
| NPS (proxy) | `mean(nps_score)` | by branch | 🟡 | KPI card |
| Complaint rate | `mean(complaint_raised)` *within feedback population* | by branch, category | 🟢 | KPI card |
| Emergency share | `mean(admission_type=='Emergency')` | by branch | 🟢 | donut |
| Feedback coverage | `has_feedback` share of admissions | overall | 🟢 | KPI card |

**Deliverable:** a one-screen "chain scorecard" (grid of KPI cards) + a branch league table ranking all 25 hospitals on 4–5 of these.

---

## Section 3 — Revenue & Financial Health *(lead domain)*

The money story. Usually the headline of a hospital-analytics portfolio — go deep.

| KPI | Formula | Cuts to show | Flag | Best visual |
|-----|---------|--------------|------|-------------|
| Gross / net revenue | `sum(gross_amount)`, `sum(net_amount)` | branch, region, tier, department, quarter, month, season | 🟢 | bar / stacked area over time |
| Revenue trend (MoM / QoQ) | `% change` of monthly/quarterly net revenue | overall, by branch | 🟢 | line + % labels |
| Service-line revenue mix | `sum(procedure/pharmacy/lab/room_charges) / sum(gross_amount)` | overall, by department | 🟢 | 100% stacked bar |
| ARPOB (revenue per occupied bed-day) | `sum(net_amount) / sum(length_of_stay)` | branch, department, ward | 🟢 | bar |
| Discount rate & leakage | `sum(discount_amount) / sum(gross_amount)`; total `discount_amount` | department, payer, branch | 🟢 | bar; treemap of ₹ leakage |
| Collection efficiency | `sum(collected_amount)/sum(net_amount)` **excl overbilled** | branch, region, payer | 🟡 | bar |
| Outstanding ratio (AR intensity) | `sum(outstanding_amount)/sum(net_amount)` **excl overbilled** | branch, payer | 🟡 | bar |
| **Overbilling audit** | `mean(overbilled_flag)`; `sum(excess_amount)` | branch, department | 🟢 | bar (a *data-integrity* KPI) |
| Revenue concentration (Pareto) | Cumulative % of revenue from top *n*% of admissions/patients | overall | 🟢 | Pareto / Lorenz curve |
| High-value case share | Share of admissions with `net_amount ≥ p90`; their revenue % | department, diagnosis | 🟢 | bar |
| Revenue by diagnosis & severity | `sum(net_amount)` by ICD `category`, `severity_level` | overall | 🟢 | treemap / bar |
| Billing lag | `mean(billing_lag_days)` | branch | 🟢 | box |
| Payer mix | Share of admissions by `insurance_type` | overall (descriptive only) | 🟡 | donut |

**Note on payer analysis:** `payer_type`, `insurance_type`, `insurance_company` and `payment_status` are all noise/contradictory. Use `insurance_type` as a *descriptive slice* only — don't build revenue-realization conclusions on it.

---

## Section 4 — Clinical Operations & Efficiency *(lead domain)*

How well the hospitals run. Blends admissions, labs, and pharmacy.

### Throughput & length of stay

| KPI | Formula | Cuts | Flag | Visual |
|-----|---------|------|------|--------|
| ALOS | `mean(length_of_stay)` | department, severity, admission_type, ward, diagnosis, branch | 🟢 | box / bar |
| LOS distribution & outliers | histogram; `p50/p90/p99`; `is_long_stay` rate | overall, by department | 🟢 | histogram + box |
| Admissions volume / throughput | `count(admission_id)` per day/week/month | branch, department | 🟢 | line / heatmap (dow × month) |
| Bed occupancy (proxy) | `sum(length_of_stay) / (bed_capacity × 365)` | branch | 🟡 (not `bed_id`) | bar |
| Bed turnover | `count(admission_id) / bed_capacity` | branch | 🟢 | bar |
| Emergency : Elective ratio | counts by `admission_type` | branch, season | 🟢 | stacked bar |

### Case mix & outcomes

| KPI | Formula | Cuts | Flag | Visual |
|-----|---------|------|------|--------|
| Ward mix | share by `ward_type` (incl. ICU %) | branch | 🟢 | 100% stacked bar |
| Diagnosis / therapeutic mix | share by ICD `category` | branch, season | 🟢 | treemap |
| Severity mix / case-mix index | share by `severity_level`; mean severity score | department | 🟢 | bar |
| Chronic-disease burden | `mean(is_chronic)` | branch, age_band | 🟢 | bar |
| Discharge outcome mix | share by `discharge_type` | department, severity | 🟢 | 100% stacked bar |
| Mortality / LAMA rate | `mean(Expired)`, `mean(LAMA)` | department, severity | 🟢 | bar |
| 30-day readmission rate | `mean(readmission_flag)` | department, diagnosis, doctor | 🟢 | bar |

### Diagnostics (lab) — analyze at `fact_lab_orders` grain

| KPI | Formula | Cuts | Flag | Visual |
|-----|---------|------|------|--------|
| Test volume & mix | `count`, share by `test_name` / `test_category` | branch | 🟢 | bar |
| Tests per admission | `test_count` mean | department | 🟢 | bar |
| Turnaround time (TAT) | `mean`/`median(tat_hours)` | test, category, branch | 🟢 | box |
| **SLA breach rate** | `mean(tat_breach_flag)` | test, category, branch | 🟢 | bar |
| Critical-result rate | `mean(result_status=='Critical')` | category | 🟢 | bar |

### Pharmacy — analyze at `fact_pharmacy_orders` grain

| KPI | Formula | Cuts | Flag | Visual |
|-----|---------|------|------|--------|
| Dispensing volume & drug-category mix | `count`, share by `drug_category` | branch | 🟢 | bar |
| Fulfillment rate | `clip(quantity_dispensed/quantity_ordered, 0, 1)` | branch, drug | 🟡 | bar |
| Stockout rate | `mean(stockout_flag)` | branch, drug_category | 🟢 | bar |
| Wastage rate | `mean(wastage_flag)` | branch, drug_category | 🟢 | bar |
| Pharmacy cost | `sum(total_cost)` | branch, drug_category | 🟢 | treemap |
| Near-expiry exposure | `days_to_expiry = expiry_date − dispensed_date`; share < 90 days | drug_category | 🟢 | histogram |
| **Clinical audit: Over-dispense** | Count & share of rows where `quantity_dispensed > quantity_ordered` | drug_category | 🟢 | bar + markdown callout with 5 clinical reasons |

### Seasonality (the real-world hospital angle)

Admissions and disease categories by `season` / `adm_month` — look for respiratory & infectious spikes in Monsoon, cardiac patterns in Winter.

**Visual:** month × diagnosis-category heatmap.

---

## Section 5 — Patient Experience & Satisfaction *(lead domain)*

Analyze on the feedback sub-population (~39,577 admissions / 33.3%). **Always caption the coverage %** so nobody reads it as the whole chain.

| KPI | Formula | Cuts | Flag | Visual |
|-----|---------|------|------|--------|
| Overall CSAT | `mean(overall_csat)` *on 1–6 Likert scale* | branch, department, ward, region | 🟡 (33% coverage) | bar / gauge |
| Touchpoint ratings | `mean` of `doctor_/nursing_/cleanliness_/food_/billing_rating` | branch, department | 🟢 (1–6 scale) | radar / grouped bar |
| NPS (proxy) | `mean(nps_score)` | branch, department | 🟡 | bar |
| Complaint rate | `mean(complaint_raised)` *within feedback population* | branch, department, ward | 🟢 | bar |
| Complaint category mix | share by `complaint_category` | overall, by branch | 🟢 | treemap |
| Satisfaction vs experience | CSAT correlated with `length_of_stay`, `tat_breach_rate`, `adverse_discharge`, `readmission_flag`, `stockout_count` | overall | 🟡 (correlational) | scatter / grouped box |
| Response / coverage rate | `has_feedback` share | branch | 🟢 | bar |

**Driver analysis is the money insight here:** does longer LOS, an SLA breach, or a stockout depress CSAT? A correlation heatmap of CSAT vs the operational features is a strong portfolio exhibit — just frame it as association, not proof.

---

## Section 6 — Workforce & Doctor Performance *(HR angle)*

⚠️ Attribute all doctor activity through `fact_admissions` (the doctor's own `department`/`hospital_id` in `dim_doctors` are 🔴 unreliable). `consultation_fee` is an **OPD** attribute — don't equate it with inpatient revenue.

| KPI | Formula | Cuts | Flag | Visual |
|-----|---------|------|------|--------|
| Headcount & structure | `nunique(doctor_id)` by `specialization`, `employment_type` | via admissions | 🟢 | bar |
| Doctor productivity | `count(admission_id) / doctor` | specialization, branch | 🟢 | bar / distribution |
| Revenue per doctor | `sum(net_amount) / doctor` | specialization | 🟢 | bar |
| Case load / utilization | admissions per doctor per month | specialization | 🟢 | box |
| Avg LOS per doctor | `mean(length_of_stay)` by doctor | within specialization | 🟢 | box |
| Outcome rates per doctor | `mean(mortality_flag)`, `mean(readmission_flag)` by doctor | within specialization | 🟢 (⚠️ **not risk-adjusted** — compare within same specialization/severity) | scatter |
| Avg doctor rating | `mean(doctor_rating)` by doctor *on 1–6 scale* | specialization | 🟡 | bar |
| Experience effect | `experience_years` vs rating / revenue / LOS | overall | 🟢 | scatter + trend |
| Fee positioning | `consultation_fee` distribution by `specialization`; fee vs volume/rating | overall | 🟢 (OPD only) | box / scatter |
| Employment-type performance | productivity & rating by Full-time / Visiting / Consultant | overall | 🟢 | grouped bar |
| Specialization supply vs demand | doctors per specialization vs admissions per matching diagnosis category | overall | 🟢 | dual bar |

---

## Section 7 — Patient Demographics & Market *(business / hospitality angle)*

Who the patients are and where they come from — the commercial and catchment view.

| KPI | Formula | Cuts | Flag | Visual |
|-----|---------|------|------|--------|
| Age distribution & band mix | `age` histogram; `age_band` share | overall, by department | 🟢 | histogram / bar |
| Gender mix | share by `gender` | department, diagnosis | 🟢 | donut; gender × dept heatmap |
| Blood-group distribution | share by `blood_group` | overall | 🟢 (ops relevance: blood bank) | bar |
| Geographic origin | patients by `state_of_residence` / `city_of_residence` | overall | 🟢 | choropleth / bar |
| Catchment flow | in-region vs out-of-region (`state_of_residence` region vs hospital `region`) | by branch | 🟢 | sankey / stacked bar |
| New vs Repeat mix | share by `patient_type`; revenue share of Repeat | branch | 🟢 | donut + bar |
| Referral-channel mix & value | share by `referral_source`; net revenue per channel | overall | 🟢 | bar |
| Insurance-type mix | share by `insurance_type` | overall (descriptive) | 🟡 | donut |
| Chronic vs acute patients | `mean(is_chronic)` at patient level | age_band, region | 🟢 | bar |

---

## Section 8 — Hierarchical & cross-cut analysis *(the "drill-down")*

Take any KPI from Sections 2–7 and roll it up or drill it down a nested structure.

### The five hierarchies on this data:

| Hierarchy | Levels (top → bottom) | Use for |
|-----------|----------------------|---------|
| Organizational / geographic | Chain → **Region** (N/S/E/W) → **State** → **City** → **Hospital** → **Department** → **Doctor** → Encounter | revenue, ALOS, CSAT, readmission — the primary drill-down |
| Facility | Region → **Tier** (1/2) → **Accreditation** (JCI / NABH / Unaccredited) → Hospital | benchmarking, "does accreditation pay off?" |
| Clinical | **Therapeutic area** (ICD `category`) → **Diagnosis** (`diagnosis_name`) → **Severity** → chronic/acute → Encounter | case mix, cost & LOS by disease |
| Service-line | **Department** → **Ward type** → **Admission type** | operational efficiency |
| Temporal | **Quarter** → **Month** → **Week** → **Day-of-week**; plus **Season** | trend & seasonality (single year — no Year level) |

**Technique:** for each headline KPI, produce the full org drill-down — Region summary, then branch-within-region, then department-within-branch — using `groupby` + `pivot_table`, and visualize with a **treemap** (hierarchical) or **small-multiple bars** (one panel per region).

### High-value two-way cross-cuts (pivot heatmaps):

`Department × Season` (seasonal demand) · `Branch × Insurance Type` (payer mix) · `Specialization × Severity` (acuity load) · `Age-band × Diagnosis category` (who gets what disease) · `Ward × CSAT` (does ICU depress satisfaction?) · `Tier × ARPOB` (Tier-1 premium?) · `Accreditation × Outcomes` (mortality/readmission) · `Region × Service-line mix`.

---

## Section 9 — The EDA methodology arc *(the disciplined order)*

Great EDA isn't a pile of plots — it's a progression from *shape* to *relationships* to *story*. Move through these phases and write a one-line "so what?" under every exhibit.

**Phase 1 — Univariate.** One variable at a time. Distributions of every measure (histogram / box / KDE — note skew & outliers); frequency of every categorical (bar / `value_counts`). Goal: know each field's shape before relating it to anything.

**Phase 2 — Bivariate.** Measure × categorical (box / violin / grouped bar), measure × measure (scatter + correlation), categorical × categorical (crosstab → heatmap). This is where most KPIs actually get computed.

**Phase 3 — Multivariate.** Numeric correlation heatmap; faceted small multiples (e.g., LOS-vs-revenue scatter, one panel per region); pivot heatmaps; controlled comparisons (compare doctors *within* a specialization, not across).

**Phase 4 — Time series.** Monthly/quarterly trends, rolling means, QoQ/MoM growth, and season × diagnosis heatmaps. *(Remember: single year — focus on monthly patterns, not multi-year trends.)*

**Phase 5 — Segmentation & synthesis.** Cohorts (age-band, payer, new/repeat), Pareto/concentration, optional clustering of the 25 branches on their KPI profile, and the hero storylines below.

### Visualization cheat-sheet

| The question | Chart |
|--------------|-------|
| Distribution of one measure | histogram / box / violin |
| Frequency of a category | bar / donut |
| A measure across categories | grouped bar / box |
| Two measures related | scatter (+ trend line) |
| Many measures' correlations | heatmap |
| Part-to-whole | 100% stacked bar / treemap |
| Trend over time | line / area |
| Two-dimension intensity | heatmap (pivot) |
| Ranking (e.g., 25 branches) | sorted bar / lollipop |
| Concentration | Pareto / Lorenz curve |
| Flow (catchment) | sankey |

---

## Section 10 — "Hero" insights to hunt *(portfolio storylines)*

Anyone can plot a bar chart. These are the *findings* that make the project memorable — each ties a real hospital-industry tension to your data:

1. **Revenue-vs-experience quadrant.** Plot each branch on ARPOB (x) vs CSAT (y). The interesting branches are high-revenue / low-satisfaction — a real strategic tension.
2. **The service-quality chain.** Does a higher lab **SLA-breach rate** track with lower CSAT and more complaints across branches? (Use the 🟢 `tat_breach_flag`.)
3. **Efficiency vs acuity.** Which branches run long ALOS *without* higher severity mix? That's avoidable cost, not sicker patients.
4. **Revenue concentration (Pareto).** What share of patients / diagnosis categories drives 80% of net revenue? Where should the chain focus?
5. **Seasonality & staffing.** Monsoon respiratory / infectious surges and Winter cardiac patterns vs doctor supply per specialization — a demand-planning story.
6. **Readmission hotspots.** Departments, diagnoses, or (within-specialization) doctors with elevated 30-day readmission — both a quality and a revenue-leakage issue.
7. **Discount leakage.** Departments/branches granting outsized discounts without a collection payoff.
8. **Accreditation & tier payoff.** Do JCI/NABH or Tier-1 branches show measurably better outcomes or satisfaction?
9. **Data-integrity exhibit.** Quantify what you caught — overbilling ₹ (`excess_amount`), invalid stockout records (52 archived), sentinel ages handled, orphaned rows cleaned. Presenting your *own* data-quality audit signals real analytical maturity.
10. **Clinical audit: Over-dispense & protocol overrides.** Present the ~1,800 dispensed > ordered rows with your 5 real-world clinical explanations — demonstrates healthcare operations domain knowledge.

Frame every correlational finding as **association, not causation** — that restraint reads as senior.

---

## Section 11 — Implementation sequence (updated)

A clean order to execute in the notebook, starting from your current position (Cell ~149):

| Step | Section | What to do |
|------|---------|------------|
| 1 | 1 | **Feature engineering** — temporal, demographic, clinical, financial, experience features |
| 2 | 2 | **Executive scorecard** — KPI cards + branch league table |
| 3 | 3 | **Revenue & finance** — deep dive into money story |
| 4 | 4 | **Clinical operations** — admissions → LOS → labs → pharmacy → seasonality |
| 5 | 5 | **Patient experience** — CSAT, NPS, complaints (always state 33.3% coverage) |
| 6 | 6 | **Workforce** — doctor productivity, experience effect, employment type |
| 7 | 7 | **Demographics & market** — age, gender, geography, catchment flow |
| 8 | 8 | **Hierarchical drill-downs & cross-cuts** — pivot heatmaps, treemaps |
| 9 | 10 | **Hero insights synthesis** — the 10 portfolio storylines |
| 10 | — | **Insight summary + data-quality appendix** — close with top findings and anomalies handled |

### Working tips
- Write one reusable helper, e.g. `kpi = df.groupby(dim).agg(...)`, and reuse it for every cut — don't hand-code 40 group-bys.
- After each chart, add a short markdown cell stating the insight ("so what?"). Recruiters read those.
- Save `admission_master` to CSV/parquet once so you don't re-merge every session. *(You've already done this — Cell 152)*
- Use one consistent color palette and always label axes, units (₹, days, %), and the denominator (esp. the feedback sub-population).
- Keep a running "data-quality log" cell — it becomes your appendix.
- Remember: single-year data (2024). Focus on monthly/quarterly/seasonal patterns, not YoY growth.

---

*Build Section 1 features first — every KPI in Sections 2–10 reads off `admission_master` and its engineered features. Reliability flags: 🟢 headline freely · 🟡 apply the noted caveat · 🔴 don't treat as meaningful.*
