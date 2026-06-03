"""
Figure 3: Division-level measles burden + Table 2.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

DATA = "/Users/khalilur/Documents/AIWORK"
OUT  = "/Users/khalilur/Documents/AIWORK/analysis/figures"

# 2022 Bangladesh Census population estimates by division
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

df = pd.read_csv(f"{DATA}/measles_division_breakdown.csv", parse_dates=["date"])
df = df[df["division"] != "Total"]

# Latest cumulative snapshot per division (use max cumulative values)
latest = (df.groupby("division")
            .agg(
                confirmed_cumulative=("confirmed_cumulative", "max"),
                suspected_cumulative=("suspected_cumulative", "max"),
                hospitalized_cumulative=("hospitalized_cumulative", "max"),
                confirmed_deaths_cumulative=("confirmed_deaths_cumulative", "max"),
                recovered_cumulative=("recovered_cumulative", "max"),
            )
            .reset_index())

latest["population"] = latest["division"].map(POPULATION)
latest["incidence_per_100k"] = (
    latest["confirmed_cumulative"] / latest["population"] * 100_000
).round(1)
latest["cfr_pct"] = (
    latest["confirmed_deaths_cumulative"] / latest["confirmed_cumulative"] * 100
).round(2)
latest["share_pct"] = (
    latest["confirmed_cumulative"] / latest["confirmed_cumulative"].sum() * 100
).round(1)

latest = latest.sort_values("confirmed_cumulative", ascending=False).reset_index(drop=True)

COLORS = ["#C0392B","#2980B9","#27AE60","#8E44AD","#E67E22","#16A085","#2C3E50","#D35400"]

# ── Figure 3: two-panel ─────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# Panel A: Confirmed cases by division
bars = ax1.barh(latest["division"][::-1], latest["confirmed_cumulative"][::-1],
                color=COLORS[:len(latest)][::-1], edgecolor="white", linewidth=0.5)
for bar, val in zip(bars, latest["confirmed_cumulative"][::-1]):
    ax1.text(val + 200, bar.get_y() + bar.get_height() / 2,
             f"{int(val):,}", va="center", ha="left", fontsize=8.5)
ax1.set_xlabel("Confirmed Cases (Cumulative)", fontsize=10)
ax1.set_title("A. Confirmed Cases by Division", fontsize=11, fontweight="bold")
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax1.spines[["top", "right"]].set_visible(False)
ax1.grid(axis="x", linestyle="--", alpha=0.35)

# Panel B: Incidence rate per 100,000
bars2 = ax2.barh(latest["division"][::-1], latest["incidence_per_100k"][::-1],
                 color=COLORS[:len(latest)][::-1], edgecolor="white", linewidth=0.5)
for bar, val in zip(bars2, latest["incidence_per_100k"][::-1]):
    ax2.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
             f"{val:.0f}", va="center", ha="left", fontsize=8.5)
ax2.set_xlabel("Incidence Rate (per 100,000 population)", fontsize=10)
ax2.set_title("B. Incidence Rate per 100,000 by Division", fontsize=11, fontweight="bold")
ax2.spines[["top", "right"]].set_visible(False)
ax2.grid(axis="x", linestyle="--", alpha=0.35)
ax2.set_yticklabels([])

fig.suptitle("Figure 3. Division-level Measles Burden, Bangladesh 2026",
             fontsize=12, fontweight="bold", y=1.01)
fig.tight_layout()
fig.savefig(f"{OUT}/fig3_division_burden.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/fig3_division_burden.png")
plt.close()

# ── Table 2 ─────────────────────────────────────────────────────────────────
t2 = latest[["division", "population", "confirmed_cumulative", "suspected_cumulative",
              "hospitalized_cumulative", "recovered_cumulative",
              "confirmed_deaths_cumulative", "incidence_per_100k",
              "cfr_pct", "share_pct"]].copy()
t2.columns = [
    "Division", "Population (2022)",
    "Confirmed Cases", "Suspected Cases",
    "Hospitalized", "Recovered",
    "Confirmed Deaths", "Incidence /100k",
    "CFR (%)", "% of National Total"
]
# Add total row
total_row = pd.DataFrame([[
    "NATIONAL TOTAL",
    sum(POPULATION.values()),
    t2["Confirmed Cases"].sum(),
    t2["Suspected Cases"].sum(),
    t2["Hospitalized"].sum(),
    t2["Recovered"].sum(),
    t2["Confirmed Deaths"].sum(),
    round(t2["Confirmed Cases"].sum() / sum(POPULATION.values()) * 100_000, 1),
    round(t2["Confirmed Deaths"].sum() / t2["Confirmed Cases"].sum() * 100, 2),
    100.0,
]], columns=t2.columns)
t2 = pd.concat([t2, total_row], ignore_index=True)

t2.to_csv(f"{DATA}/analysis/table2_division_stats.csv", index=False)
print(f"\nTable 2 saved: {DATA}/analysis/table2_division_stats.csv")
print(t2.to_string(index=False))
