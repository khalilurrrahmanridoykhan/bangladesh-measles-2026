"""
Spatial Analysis - Figure 3: Temporal progression maps (weekly)
Shows how the outbreak spread geographically across 8 weeks
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import warnings
warnings.filterwarnings("ignore")

SHP   = "/Users/khalilur/Documents/GMGI/ewars/src/assets/data/extracted_shapefile/bd_adm3_output_shapefile.shp"
DGHS  = "/Users/khalilur/Documents/AIWORK/measles_division_breakdown.csv"
OUT   = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

# ── Load shapefile — dissolve to division level ──────────────────────────────
gdf = gpd.read_file(SHP)
gdf_div = gdf.dissolve(by="division", aggfunc="sum").reset_index()[["division","geometry"]]

# ── Load DGHS division data and standardise names ────────────────────────────
df = pd.read_csv(DGHS, parse_dates=["date"])
name_map = {
    "Chattogram": "Chittagong",
    "Barishal":   "Barisal",
}
df["division"] = df["division"].replace(name_map)
df = df.sort_values("date")

# Assign epidemiological week (Week 1 = first 7 days)
start_date = df["date"].min()
df["epi_week"] = ((df["date"] - start_date).dt.days // 7) + 1

# Aggregate weekly cumulative: use last day of each week per division
weekly = (
    df.groupby(["epi_week","division"])
    .agg(cum_suspected=("suspected_cumulative","max"),
         cum_confirmed=("confirmed_cumulative","max"))
    .reset_index()
)

# Population lookup
pop = {
    "Dhaka": 34991374, "Chittagong": 29898241, "Rajshahi": 19894849,
    "Rangpur": 17363512, "Khulna": 15627710, "Sylhet": 12176958,
    "Mymensingh": 11809762, "Barisal": 8110723
}
weekly["population"] = weekly["division"].map(pop)
weekly["incidence_per100k"] = weekly["cum_suspected"] / weekly["population"] * 100000

# ── Pick 8 representative weeks ──────────────────────────────────────────────
all_weeks = sorted(weekly["epi_week"].unique())
n_weeks = min(8, len(all_weeks))
step = max(1, len(all_weeks) // n_weeks)
selected_weeks = all_weeks[::step][:n_weeks]

cmap = LinearSegmentedColormap.from_list("wred", ["#fff7ec","#fee8c8","#fdd49e",
                                                   "#fdbb84","#fc8d59","#ef6548",
                                                   "#d7301f","#990000"])
global_max = weekly["incidence_per100k"].max()
norm = mcolors.Normalize(vmin=0, vmax=global_max)

ncols = 4
nrows = (n_weeks + ncols - 1) // ncols
fig, axes = plt.subplots(nrows, ncols, figsize=(18, nrows * 4.5))
axes = axes.flatten()

for idx, week in enumerate(selected_weeks):
    ax = axes[idx]
    wdata = weekly[weekly["epi_week"] == week].copy()
    merged = gdf_div.merge(wdata[["division","incidence_per100k","cum_suspected"]],
                           on="division", how="left")
    merged["incidence_per100k"] = merged["incidence_per100k"].fillna(0)

    merged.plot(column="incidence_per100k", ax=ax, cmap=cmap, norm=norm,
                linewidth=0.7, edgecolor="white")

    # Division value labels
    label_coords = {
        "Dhaka": (90.38, 23.75), "Chittagong": (91.75, 22.70),
        "Rajshahi": (88.90, 24.45), "Khulna": (89.35, 22.70),
        "Barisal": (90.20, 22.35), "Sylhet": (91.90, 24.45),
        "Mymensingh": (90.40, 24.80), "Rangpur": (89.20, 25.75),
    }
    for _, row in merged.iterrows():
        div = row["division"]
        val = row["incidence_per100k"]
        if div in label_coords and val > 0:
            x, y = label_coords[div]
            ax.annotate(f"{val:.0f}", xy=(x, y), fontsize=6, ha="center",
                        va="center", fontweight="bold", color="black",
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.6, lw=0))

    total_cases = int(wdata["cum_suspected"].sum()) if len(wdata) > 0 else 0
    week_date = start_date + pd.Timedelta(weeks=week - 1)
    ax.set_title(f"Week {week}  ({week_date.strftime('%d %b')})\nTotal: {total_cases:,} cases",
                 fontsize=9, fontweight="bold")
    ax.set_axis_off()

# Hide unused axes
for idx in range(len(selected_weeks), len(axes)):
    axes[idx].set_axis_off()

# Shared colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.25, 0.02, 0.5, 0.018])
cb = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
cb.set_label("Suspected Incidence per 100,000 Population (Cumulative)", fontsize=9)

fig.suptitle(
    "Figure 3. Temporal Progression of the 2026 Measles Outbreak in Bangladesh\n"
    "Weekly Cumulative Incidence per 100,000 Population by Division",
    fontsize=13, fontweight="bold", y=1.01
)
plt.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig(f"{OUT}/fig3_temporal_progression.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/fig3_temporal_progression.png")
plt.close()
