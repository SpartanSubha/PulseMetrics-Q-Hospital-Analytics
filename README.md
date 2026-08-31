# 🏥 PulseMetrics-Q — Hospital Chain Quarterly Analytics

> **End-to-end Python analytics project simulating quarterly performance intelligence  
> for a 25-branch pan-India hospital chain**

---

## 📌 Project Overview

**PulseMetrics-Q** is a portfolio-grade healthcare analytics project built entirely in Python.  
It simulates the quarterly performance reporting of a Manipal-scale hospital chain — covering  
data engineering, clinical data quality auditing, multi-domain EDA, and actionable insight delivery.

**Why synthetic data?**  
Real patient data is protected under clinical privacy regulations. This dataset replicates the  
*statistical properties, domain logic, and realistic messiness* of live hospital operations data —  
making it valid for portfolio-grade analytics work.

---

## 🏗️ Dataset Architecture

| Table | Rows | Role |
|---|---|---|
| `dim_hospitals` | 25 | 25 branches across India (Tier-1 & Tier-2 cities) |
| `dim_patients` | ~60,300 | Unique patient master with demographics |
| `dim_doctors` | 800 | Doctor, specialization & department reference |
| `dim_icd_codes` | 57 | Diagnosis classification (ICD-10) |
| `fact_admissions` | ~120,600 | Core admission records — the central fact table |
| `fact_billing` | ~120,000 | Revenue, collection & payer records |
| `fact_lab_orders` | 200,000 | Lab test, TAT & result records |
| `fact_pharmacy_orders` | 180,000 | Drug dispensing & stockout records |
| `fact_patient_feedback` | 40,000 | CSAT, NPS & complaint survey data |

**Total: ~720,000+ rows across 9 interlinked tables**

---

## 🔬 Data Generator — What Makes This Realistic (v3)

The dataset is generated with domain-aware non-uniform distributions, not random noise:

| Feature | How it's simulated |
|---|---|
| **Seasonal admissions** | Monthly volume shaped by Indian hospital seasonality (±15% MoM) |
| **Weekday bias** | Weekday:Weekend admission ratio ~1.1:0.75 (mirrors real elective scheduling) |
| **Center of Excellence profiles** | Each hospital has a dominant department specialty |
| **Gender-biased departments** | Gynecology → Female patients; Urology → Male skew |
| **Revenue seasonality** | Charges vary by admission month (monsoon, winter peaks) |
| **Payer-specific discounts** | Self-Pay 0–5%, Govt 15–25% |
| **Payer × Tier collection rates** | Cashless ~93%, Govt ~75% |
| **Variable billing lag** | Day-care 0–1d, ICU 2–7d, Tier-2 hospitals +0–2d |
| **Test-specific result distributions** | CBC 5% Critical, Troponin 25% Critical |
| **Bimodal age distribution** | Paediatric peak + middle-age bulk (realistic for India) |
| **Severity-linked outcomes** | Mortality & readmission correlated with severity, not random |

---

## 🔍 Dirty Data Engineered In

Every anomaly below was intentionally injected for the data quality audit exercise:

| Table | Issue | Approx. Volume |
|---|---|---|
| `fact_admissions` | Discharge before admission date | ~1% of rows |
| `fact_admissions` | Missing `bed_id` | ~3% of rows |
| `fact_admissions` | Duplicate admission IDs | ~0.5% of rows |
| `fact_billing` | Collected amount > Net amount (overbilling) | ~2% of rows |
| `fact_lab_orders` | Report delivered before sample collected | ~1.5% of rows |
| `fact_lab_orders` | Missing `tat_hours` | ~2% of rows |
| `fact_pharmacy_orders` | Qty dispensed > Qty ordered | ~1% of rows |
| `fact_patient_feedback` | NPS score outside −100/+100 range | ~1% of rows |
| `dim_patients` | Invalid age (≤0 or >110) | ~0.8% of rows |
| `dim_patients` | Near-duplicate patient records | ~0.5% of rows |

---

## 📊 EDA Domains Covered (8 Modules)

| # | Domain | Key KPIs |
|---|---|---|
| 1 | **Executive Scorecard** | Total admissions, unique patients, net revenue, collection rate, ALOS, bed occupancy, CSAT, NPS |
| 2 | **Revenue & Financial Analysis** | ARPOB, gross/net revenue, MoM/QoQ trends, service-line mix, discount leakage, overbilling audit, billing lag |
| 3 | **Clinical Operations & Efficiency** | ALOS, LOS distribution, bed occupancy proxy, throughput, case mix, mortality & LAMA rates, 30-day readmission, lab TAT & SLA breach, pharmacy stockout & wastage |
| 4 | **Patient Experience & Satisfaction** | CSAT by branch/dept/doctor, NPS (proxy), complaint rate & category mix, experience driver analysis |
| 5 | **Workforce & Doctor Performance** | Headcount, doctor productivity, revenue per doctor, outcome rates by doctor, experience vs rating, fee positioning |
| 6 | **Patient Demographics & Market** | Age & gender distribution, blood group, geographic origin, catchment flow, new vs repeat mix, referral channel mix |
| 7 | **Hierarchical Drill-Downs** | Region → State → City → Hospital → Department → Doctor drill-down on all KPIs; pivot heatmaps; Pareto/concentration |
| 8 | **Hero Insights Synthesis** | Revenue-vs-experience quadrant, service-quality chain, efficiency vs acuity, readmission hotspots, seasonality & staffing |

---

## 📁 Project Structure

```
PulseMetrics-Q/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   └── data_generator.py              ← Reproducible data generation (v3)
│
├── data/
│   ├── raw/                           ← Generated CSVs — gitignored (size)
│   └── clean/                         ← Post-audit cleaned CSVs — gitignored
│
├── notebooks/
│   ├── 01_data_generation.ipynb       ✅ Schema walkthrough & dirty data preview
│   ├── 02_data_quality_audit.ipynb    ✅ Cleaning, anomaly handling, master table
│   ├── 03_revenue_financial.ipynb     🔄 Revenue cycle EDA (in progress)
│   ├── 04_clinical_operations.ipynb   📋 Planned
│   ├── 05_patient_experience.ipynb    📋 Planned
│   ├── 06_workforce_doctors.ipynb     📋 Planned
│   ├── 07_demographics_market.ipynb   📋 Planned
│   ├── 08_hierarchical_drilldown.ipynb📋 Planned
│   └── 09_hero_insights.ipynb         📋 Planned
│
├── outputs/
│   ├── figures/                       ← Saved chart PNGs by notebook
│   └── reports/                       ← Exported insight summaries
│
└── docs/
    ├── EDA_Roadmap.md                 ← KPI playbook & analysis blueprint
    └── data_quality_log.md            ← Running audit log of anomalies
```

---

## ⚙️ Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/SpartanSubha/PulseMetrics-Q.git
cd PulseMetrics-Q

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate all 9 datasets (~2 minutes)
python src/data_generator.py

# 4. Launch Jupyter
jupyter notebook notebooks/
```

Start with `01_data_generation.ipynb` for the schema walkthrough,  
then `02_data_quality_audit.ipynb` for the full cleaning pipeline.

---

## 🛠️ Tech Stack

`Python 3.12` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `Jupyter Notebook`

---

## 📈 Project Status

| Notebook | Status |
|---|---|
| 01 — Data Generation & Schema | ✅ Complete |
| 02 — Data Quality Audit & Master Table | ✅ Complete |
| 03 — Revenue & Financial Analysis | 🔄 In Progress |
| 04 — Clinical Operations & Efficiency | 📋 Planned |
| 05 — Patient Experience & Satisfaction | 📋 Planned |
| 06 — Workforce & Doctor Performance | 📋 Planned |
| 07 — Demographics & Market | 📋 Planned |
| 08 — Hierarchical Drill-Downs | 📋 Planned |
| 09 — Hero Insights & Synthesis | 📋 Planned |

---

## 👤 Author

**Subhabrata**  
MBA (Marketing & Operations) · Data & Business Analytics  
📧 kitusahoo@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/subhabrata99) · [GitHub](https://github.com/SpartanSubha)

---

*Building in public — follow the journey on LinkedIn: [#PulseMetricsQ](https://www.linkedin.com/search/results/content/?keywords=%23PulseMetricsQ)*
