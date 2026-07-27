"""
Spatial Analysis - Figure 11: Historical measles context (Bangladesh 2010-2026)
Data: WHO GHO WHS3_62 confirmed reported cases + 2026 DGHS data
Shows 2026 as unprecedented outbreak vs prior decade baseline.
"""

import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings("ignore")

OUT = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

# ── Fetch WHO GHO historical data for Bangladesh ──────────────────────────────
def fetch_who_gho():
    url = "https://ghoapi.azureedge.net/api/WHS3_62"
    params = {"$filter": "SpatialDim eq 'BGD'"}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    records = r.json().get("value", [])
    data = {}
    for rec in records:
        yr = rec.get("TimeDim")
        val = rec.get("NumericValue")
        if yr and val is not None:
            data[int(yr)] = int(val)
    return data

print("Fetching WHO GHO Bangladesh measles data...")
who_data = fetch_who_gho()
print("WHO data fetched:", {k: who_data[k] for k in sorted(who_data) if k >= 2010})

# ── Build dataset 2010-2025 from WHO + 2026 from DGHS ───────────────────────
years_hist = list(range(2010, 2025))
cases_who  = [who_data.get(y, 0) for y in years_hist]

# 2026 DGHS data (partial year: 2 April - 21 June 2026)
year_2026       = 2026
suspected_2026  = 92790    # total suspected (as of 21 June 2026)
confirmed_2026  = 11011    # lab-confirmed (as of 21 June 2026)

# Decade mean (2015-2024)
decade_mean = np.mean([who_data.get(y,0) for y in range(2015,2025)])

print(f"\n2010-2024 range: {min(cases_who)}-{max(cases_who)}")
print(f"Decade mean (2015-2024): {decade_mean:.0f}")
print(f"2026 confirmed: {confirmed_2026:,} (81-day period Apr-Jun)")
print(f"2026 suspected: {suspected_2026:,}")

# ── FIGURE 11: 2-panel historical comparison ─────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7),
                                gridspec_kw={"width_ratios": [2, 1]})

# ── Panel A: Full time series 2010-2026 ──────────────────────────────────────
all_years  = years_hist + [year_2026]
all_cases  = cases_who  + [confirmed_2026]

bar_colors = ["#9ecae1" if y < 2026 else "#a50f15" for y in all_years]
bar_alpha  = [0.85 if y < 2026 else 1.0 for y in all_years]

bars = ax1.bar(all_years, all_cases,
               color=bar_colors, edgecolor="white", linewidth=0.6,
               width=0.75)

# Add suspected cases as a stacked extension for 2026
ax1.bar([year_2026], [suspected_2026 - confirmed_2026],
        bottom=[confirmed_2026],
        color="#fc9272", edgecolor="white", linewidth=0.6, width=0.75,
        label="2026 Suspected (non-confirmed)")

# Decade mean line (2015-2024)
ax1.axhline(decade_mean, color="#2c7bb6", linewidth=1.5, linestyle="--",
            label=f"Decade mean 2015-2024 ({decade_mean:.0f})")

# Value labels on bars
for yr, val in zip(all_years, all_cases):
    if val > 0:
        ax1.text(yr, val + 400, f"{val:,}", ha="center", va="bottom",
                 fontsize=7, rotation=45, color="#333333")
# 2026 suspected total label
ax1.text(year_2026, suspected_2026 + 1500,
         f"Suspected:\n{suspected_2026:,}",
         ha="center", va="bottom", fontsize=8, color="#a50f15",
         fontweight="bold")

# Annotation: 2026 ratio
ratio = confirmed_2026 / decade_mean
ax1.annotate(
    f"2026 confirmed cases\n({confirmed_2026:,}) = {ratio:.0f}x\ndecade mean",
    xy=(year_2026, confirmed_2026),
    xytext=(year_2026 - 4.5, confirmed_2026 * 0.6),
    arrowprops=dict(arrowstyle="->", color="#a50f15", lw=1.5),
    fontsize=9, color="#a50f15", fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#a50f15", alpha=0.9),
)

legend_items = [
    mpatches.Patch(color="#9ecae1", label="2010-2025 Confirmed Cases (WHO GHO)"),
    mpatches.Patch(color="#a50f15", label="2026 Confirmed Cases (DGHS)"),
    mpatches.Patch(color="#fc9272", label="2026 Additional Suspected Cases"),
    Line2D([0],[0], color="#2c7bb6", linestyle="--", lw=1.5,
           label=f"Decade mean 2015-2024 ({decade_mean:.0f})"),
]
ax1.legend(handles=legend_items, fontsize=8.5, loc="upper left", framealpha=0.9)
ax1.set_xlabel("Year", fontsize=11)
ax1.set_ylabel("Reported Measles Cases", fontsize=11)
ax1.set_title("(a) Annual Reported Measles Cases, Bangladesh (2010-2026)\n"
              "2026 data: DGHS press releases (2 April - 21 June, partial year)",
              fontsize=10, fontweight="bold")
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{int(v):,}"))
ax1.set_xticks(all_years)
ax1.set_xticklabels([str(y) for y in all_years], rotation=45, ha="right", fontsize=9)
ax1.spines[["top","right"]].set_visible(False)
ax1.grid(axis="y", alpha=0.25)

# ── Panel B: Fold-change comparison bar ──────────────────────────────────────
comparators = {
    "vs 2024\n(prior year)":   (confirmed_2026, who_data.get(2024, 1)),
    "vs 2023":                 (confirmed_2026, who_data.get(2023, 1)),
    "vs 2015-2024\ndecade mean": (confirmed_2026, decade_mean),
    "vs 2010-2024\nall-time mean": (
        confirmed_2026,
        np.mean([who_data.get(y,0) for y in range(2010,2025)])
    ),
}
comp_labels  = list(comparators.keys())
fold_changes = [v[0]/max(v[1],1) for v in comparators.values()]
bar_colors2  = ["#fd8d3c","#e6550d","#a50f15","#67000d"]

bh = ax2.barh(range(len(comp_labels)), fold_changes, color=bar_colors2,
              edgecolor="white", linewidth=0.5, height=0.55)
ax2.set_yticks(range(len(comp_labels)))
ax2.set_yticklabels(comp_labels, fontsize=10)
ax2.set_xlabel("Fold Increase (2026 Confirmed vs Comparator)", fontsize=10)
ax2.axvline(1, color="grey", lw=0.8, linestyle=":")

for bar, fc, (_, (num, den)) in zip(bh, fold_changes, comparators.items()):
    ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
             f"x{fc:.0f}  ({int(den):,} → {int(num):,})",
             va="center", fontsize=9, fontweight="bold", color="#333333")

ax2.set_title("(b) 2026 Outbreak Magnitude\nRelative to Historical Baselines",
              fontsize=10, fontweight="bold")
ax2.set_xlim(0, max(fold_changes) * 1.5)
ax2.spines[["top","right"]].set_visible(False)
ax2.grid(axis="x", alpha=0.2)

fig.suptitle(
    "Figure 11. Historical Context: The 2026 Bangladesh Measles Outbreak in Perspective\n"
    "Source: WHO Global Health Observatory (WHS3_62) 2010-2024; DGHS Bangladesh 2026",
    fontsize=12, fontweight="bold", y=1.02,
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig11_historical_context.png", dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT}/fig11_historical_context.png")
plt.close()

# Save table
import pandas as pd
hist_df = pd.DataFrame({"Year": all_years, "Confirmed_Cases_WHO": all_cases})
hist_df.loc[hist_df["Year"] == 2026, "Confirmed_Cases_WHO"] = confirmed_2026
hist_df["Suspected_2026_Only"] = 0
hist_df.loc[hist_df["Year"] == 2026, "Suspected_2026_Only"] = suspected_2026
hist_df.to_csv(
    "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_historical_cases.csv",
    index=False,
)
print("Historical table saved.")
