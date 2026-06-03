"""
Figure 4: Vaccination coverage (%) vs incidence rate per 100k by division.
Vaccination data from the June 2 PDF (most complete).
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

DATA = "/Users/khalilur/Documents/AIWORK"
OUT  = "/Users/khalilur/Documents/AIWORK/analysis/figures"

# Vaccination coverage from June 2 press release PDF (hardcoded from PDF extract)
# Source: হাম রুবেলা ক্যাম্পেইন ২০২৬ — division-level targets and achieved
VACC = {
    "Barishal":    {"target": 1_063_638, "vaccinated": 1_069_949, "coverage": 101},
    "Chattogram":  {"target": 4_296_218, "vaccinated": 4_439_910, "coverage": 103},
    "Dhaka":       {"target": 4_449_632, "vaccinated": 4_587_126, "coverage": 103},
    "Khulna":      {"target": 1_614_273, "vaccinated": 1_630_128, "coverage": 101},
    "Mymensingh":  {"target": 1_330_655, "vaccinated": 1_350_674, "coverage": 102},
    "Rajshahi":    {"target": 2_048_435, "vaccinated": 2_115_216, "coverage": 103},
    "Rangpur":     {"target": 1_888_247, "vaccinated": 1_943_327, "coverage": 103},
    "Sylhet":      {"target": 1_323_966, "vaccinated": 1_315_951, "coverage":  99},
}

POPULATION = {
    "Dhaka":      36_054_418,
    "Chattogram": 28_423_019,
    "Rajshahi":   18_484_858,
    "Khulna":     15_563_000,
    "Barishal":    8_325_666,
    "Sylhet":     10_009_239,
    "Rangpur":    15_665_000,
    "Mymensingh": 11_370_000,
}

# Division confirmed cumulative from division breakdown
div_df = pd.read_csv(f"{DATA}/measles_division_breakdown.csv")
div_df = div_df[div_df["division"] != "Total"]
confirmed_by_div = (div_df.groupby("division")["confirmed_cumulative"].max().reset_index())

rows = []
for div, vdata in VACC.items():
    pop = POPULATION[div]
    conf_row = confirmed_by_div[confirmed_by_div["division"] == div]
    confirmed = int(conf_row["confirmed_cumulative"].values[0]) if len(conf_row) else 0
    incidence = round(confirmed / pop * 100_000, 1)
    rows.append({
        "Division": div,
        "Coverage (%)": vdata["coverage"],
        "Target": vdata["target"],
        "Vaccinated": vdata["vaccinated"],
        "Confirmed Cases": confirmed,
        "Population": pop,
        "Incidence /100k": incidence,
    })

vdf = pd.DataFrame(rows)

coverage = vdf["Coverage (%)"].values
incidence = vdf["Incidence /100k"].values
slope, intercept, r, p, se = stats.linregress(coverage, incidence)

COLORS = ["#C0392B","#2980B9","#27AE60","#8E44AD","#E67E22","#16A085","#2C3E50","#D35400"]

fig, ax = plt.subplots(figsize=(9, 6))

for i, row in vdf.iterrows():
    ax.scatter(row["Coverage (%)"], row["Incidence /100k"],
               s=row["Confirmed Cases"] / 60, color=COLORS[i],
               alpha=0.85, edgecolors="white", linewidth=0.8, zorder=3)
    ax.annotate(row["Division"],
                xy=(row["Coverage (%)"], row["Incidence /100k"]),
                xytext=(4, 4), textcoords="offset points",
                fontsize=9, color=COLORS[i], fontweight="bold")

# Regression line
x_range = np.linspace(coverage.min() - 0.5, coverage.max() + 0.5, 100)
ax.plot(x_range, slope * x_range + intercept,
        color="grey", linestyle="--", linewidth=1.5, alpha=0.7, zorder=2)

# Annotations
ax.text(0.97, 0.97,
        f"r = {r:.2f},  p = {p:.3f}\n(Pearson correlation)",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=10, color="grey",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
ax.text(0.97, 0.84,
        "Bubble size ∝ confirmed cases",
        transform=ax.transAxes, ha="right", va="top", fontsize=8.5, color="grey")

ax.set_xlabel("Measles-Rubella Campaign 2026 Coverage (%)", fontsize=11)
ax.set_ylabel("Confirmed Measles Incidence (per 100,000 population)", fontsize=11)
ax.set_title("Figure 4. Measles-Rubella Vaccine Coverage vs. Measles Incidence\n"
             "by Division, Bangladesh 2026", fontsize=12, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(linestyle="--", alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT}/fig4_vaccination_vs_incidence.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/fig4_vaccination_vs_incidence.png")
plt.close()

# Save data table
vdf.to_csv(f"{DATA}/analysis/table_vaccination_division.csv", index=False)
print(f"\nVaccination table saved.")
print(vdf[["Division","Coverage (%)","Confirmed Cases","Incidence /100k"]].to_string(index=False))
print(f"\nPearson r={r:.3f}, p={p:.3f}")
