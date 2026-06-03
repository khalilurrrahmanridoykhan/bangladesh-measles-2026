# Bangladesh Measles Outbreak 2026 — Data & Analysis

This repository contains the data, analysis scripts, and figures for the research paper:

> **"Epidemiology of the 2026 Measles Outbreak in Bangladesh: A Descriptive Analysis of National Surveillance Data with Vaccine Coverage Assessment"**
>
> Khalilur Rahman Ridoy Khan — East West University, Dhaka, Bangladesh

---

## Key Findings

| Metric | Value |
|--------|-------|
| Reporting period | 2 April – 2 June 2026 (62 days) |
| Total suspected cases | 73,362 |
| Total confirmed cases | 9,136 |
| Confirmation rate | 12.5% |
| Suspected deaths | 504 |
| Confirmed deaths | 90 |
| Case fatality rate (confirmed) | 0.99% |
| Peak daily suspected cases | 1,503 (10 May 2026) |
| Doubling time (early phase) | 6.1 days |
| National vaccination coverage (MR Campaign 2026) | 102% |

---

## Data Source

All data is sourced from publicly available daily press release PDFs published by the **Directorate General of Health Services (DGHS), Bangladesh**:

- URL: https://dghs.gov.bd/pages/press-releases/
- Data collected: 2 April 2026 to 2 June 2026
- PDF host: Oracle Cloud Storage (linked from DGHS press release pages)
- No patient-level or identifiable data is used — all data is aggregated at national and division level

---

## Repository Structure

```
bangladesh-measles-2026/
├── data/
│   ├── measles_national_summary.csv       # 62-day daily national data
│   ├── measles_division_breakdown.csv     # Division-level daily data (8 divisions)
│   ├── table1_summary_stats.csv           # Table 1: National summary statistics
│   ├── table2_division_stats.csv          # Table 2: Division-level burden
│   ├── table3_dynamics_summary.csv        # Table 3: Outbreak dynamics
│   ├── table3_dynamics_weekly.csv         # Weekly breakdown
│   └── table_vaccination_division.csv     # MR Campaign 2026 coverage by division
├── scripts/
│   ├── dghs_measles_full.py               # Web scraper (collects data from DGHS)
│   ├── fix_deaths.py                      # Patches deaths columns from PDFs
│   ├── 01_epidemic_curve.py               # Figure 1: Epidemic curve
│   ├── 02_cumulative_trajectory.py        # Figure 2 + Table 1
│   ├── 03_division_analysis.py            # Figure 3 + Table 2
│   ├── 04_vaccination_vs_cases.py         # Figure 4
│   └── 05_outbreak_dynamics.py            # Table 3 + Figure S1
├── figures/
│   ├── fig1_epidemic_curve.png
│   ├── fig2_cumulative_trajectory.png
│   ├── fig3_division_burden.png
│   ├── fig4_vaccination_vs_incidence.png
│   └── figS1_weekly_dynamics.png
└── paper/                                 # Manuscript files (Word/PDF)
```

---

## How to Reproduce

```bash
# 1. Install dependencies
pip install requests beautifulsoup4 pdfplumber pandas matplotlib seaborn scipy openpyxl

# 2. Collect data (re-scrapes all press releases)
python scripts/dghs_measles_full.py

# 3. Fix deaths columns
python scripts/fix_deaths.py

# 4. Generate all figures and tables
python scripts/01_epidemic_curve.py
python scripts/02_cumulative_trajectory.py
python scripts/03_division_analysis.py
python scripts/04_vaccination_vs_cases.py
python scripts/05_outbreak_dynamics.py
```

---

## Population Data

Division population estimates from the **Bangladesh Population and Housing Census 2022**
(Bangladesh Bureau of Statistics):

| Division | Population |
|----------|-----------|
| Dhaka | 36,054,418 |
| Chattogram | 28,423,019 |
| Rajshahi | 18,484,858 |
| Khulna | 15,563,000 |
| Rangpur | 15,665,000 |
| Mymensingh | 11,370,000 |
| Sylhet | 10,009,239 |
| Barishal | 8,325,666 |

---

## License

Data: Public domain (Government of Bangladesh, DGHS)  
Code: MIT License  
Paper: CC BY 4.0

---

## Citation

If you use this data or code, please cite:

> Ridoy Khan KR. Epidemiology of the 2026 Measles Outbreak in Bangladesh: A Descriptive Analysis of National Surveillance Data with Vaccine Coverage Assessment. *medRxiv* [Preprint]. 2026. doi: [to be assigned]
