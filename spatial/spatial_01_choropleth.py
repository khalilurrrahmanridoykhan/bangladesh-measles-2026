"""
Spatial Analysis - Figure 1: Division-level choropleth maps
4-panel: suspected incidence, confirmed incidence, CFR, hospitalization rate
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings("ignore")

SHP = "/Users/khalilur/Documents/GMGI/ewars/src/assets/data/extracted_shapefile/bd_adm3_output_shapefile.shp"
DATA = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/division_measles_complete.csv"
OUT  = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

# ── Load and prepare data ────────────────────────────────────────────────────
gdf = gpd.read_file(SHP)
gdf = gdf.dissolve(by="division", aggfunc="sum").reset_index()
gdf = gdf[["division", "geometry"]]

df = pd.read_csv(DATA)
df["suspected_incidence"]   = df["suspected_total"]   / df["population_2022"] * 100000
df["confirmed_incidence"]   = df["confirmed_total"]   / df["population_2022"] * 100000
df["cfr_confirmed"]         = df["confirmed_deaths"]  / df["confirmed_total"] * 100
df["hospitalization_rate"]  = df["hospitalized_total"]/ df["suspected_total"] * 100

merged = gdf.merge(df, on="division", how="left")

# ── Division label centroids ─────────────────────────────────────────────────
label_coords = {
    "Dhaka":      (90.38, 23.75),
    "Chittagong": (91.75, 22.70),
    "Rajshahi":   (88.90, 24.45),
    "Khulna":     (89.35, 22.70),
    "Barisal":    (90.20, 22.35),
    "Sylhet":     (91.90, 24.45),
    "Mymensingh": (90.40, 24.80),
    "Rangpur":    (89.20, 25.75),
}

# ── Color maps ───────────────────────────────────────────────────────────────
cmap_red   = LinearSegmentedColormap.from_list("wred",  ["#fef0d9","#d7301f"])
cmap_blue  = LinearSegmentedColormap.from_list("wblue", ["#eff3ff","#084594"])
cmap_green = LinearSegmentedColormap.from_list("wgrn",  ["#f7fcf5","#005a32"])
cmap_orng  = LinearSegmentedColormap.from_list("worng", ["#fff5eb","#7f2704"])

panels = [
    ("suspected_incidence",  "Suspected Cases per 100,000", cmap_red,   "(a)"),
    ("confirmed_incidence",  "Confirmed Cases per 100,000", cmap_blue,  "(b)"),
    ("cfr_confirmed",        "Case Fatality Rate (%)",      cmap_orng,  "(c)"),
    ("hospitalization_rate", "Hospitalization Rate (%)",    cmap_green, "(d)"),
]

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
axes = axes.flatten()

for ax, (col, title, cmap, panel_label) in zip(axes, panels):
    vmin = merged[col].min()
    vmax = merged[col].max()
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    merged.plot(column=col, ax=ax, cmap=cmap, linewidth=0.8,
                edgecolor="white", legend=False)

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02)
    cb.ax.tick_params(labelsize=8)

    # Division labels with value
    for _, row in merged.iterrows():
        div = row["division"]
        val = row[col]
        if div in label_coords:
            x, y = label_coords[div]
            ax.annotate(f"{div}\n{val:.1f}",
                        xy=(x, y), fontsize=6.5, ha="center", va="center",
                        fontweight="bold", color="black",
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7, lw=0))

    ax.set_title(f"{panel_label} {title}", fontsize=11, fontweight="bold", pad=8)
    ax.set_axis_off()

fig.suptitle(
    "Figure 1. Geographic Distribution of the 2026 Measles Outbreak in Bangladesh\n"
    "by Administrative Division (n=8)",
    fontsize=13, fontweight="bold", y=0.98
)
plt.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(f"{OUT}/fig1_choropleth_maps.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/fig1_choropleth_maps.png")
plt.close()

# ── Print division stats table ───────────────────────────────────────────────
print("\nDivision Summary Table:")
cols = ["division","suspected_total","confirmed_total","suspected_incidence",
        "confirmed_incidence","cfr_confirmed","hospitalization_rate"]
tbl = df[cols].sort_values("suspected_incidence", ascending=False)
tbl.columns = ["Division","Suspected","Confirmed","Suspected/100k","Confirmed/100k","CFR(%)","Hosp Rate(%)"]
for c in ["Suspected/100k","Confirmed/100k","CFR(%)","Hosp Rate(%)"]:
    tbl[c] = tbl[c].round(1)
print(tbl.to_string(index=False))
tbl.to_csv("/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_spatial_division.csv", index=False)
