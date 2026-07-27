"""
Spatial Analysis - Figure 9: Upazila-level population density surface
499 upazilas from the national Level-3 shapefile with 2022 Census population.
Computed in UTM Zone 46N (EPSG:32646) for accurate planar area.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

SHP = "/Users/khalilur/Documents/GMGI/ewars/src/assets/data/extracted_shapefile/bd_adm3_output_shapefile.shp"
DATA = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/division_measles_complete.csv"
OUT  = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

# ── Load shapefile and compute upazila-level population density ──────────────
gdf = gpd.read_file(SHP)
gdf_proj = gdf.to_crs("EPSG:32646")          # UTM 46N for accurate area
gdf_proj["area_km2"] = gdf_proj.geometry.area / 1e6
gdf_proj["pop_density"] = gdf_proj["2022"] / gdf_proj["area_km2"]

# Back to WGS84 for plotting
gdf_wgs = gdf_proj.to_crs("EPSG:4326")

# Division boundaries for overlay
gdf_div = gdf_wgs.dissolve(by="division").reset_index()[["division","geometry"]]

# ── Division-level density for comparison bar ────────────────────────────────
div_stats = gdf_proj.groupby("division").agg(
    pop_2022=("2022", "sum"),
    area_km2=("area_km2", "sum")
).reset_index()
div_stats["div_density"] = div_stats["pop_2022"] / div_stats["area_km2"]

# Merge incidence for colour coding the bar chart
case_df = pd.read_csv(DATA)
case_df["suspected_incidence"] = case_df["suspected_total"] / case_df["population_2022"] * 100000
div_stats = div_stats.merge(case_df[["division","suspected_incidence"]], on="division", how="left")

print("Upazila count:", len(gdf_wgs))
print("\nDivision density (persons/km2):")
print(div_stats[["division","pop_2022","area_km2","div_density","suspected_incidence"]].round(1).to_string(index=False))

# ── FIGURE 9: 3-panel ─────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 9))
gs = fig.add_gridspec(1, 3, wspace=0.06, width_ratios=[3, 3, 2])
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
ax3 = fig.add_subplot(gs[2])

# ── Panel A: Upazila population density choropleth ───────────────────────────
cmap_pur = LinearSegmentedColormap.from_list("pur",
    ["#f7f4f9","#d4b9da","#c994c7","#df65b0","#e7298a","#ce1256","#91003f"])
# Use log scale for density to handle skewness
gdf_wgs["log_density"] = np.log1p(gdf_wgs["2022"] / gdf_proj["area_km2"])

vmin = gdf_wgs["log_density"].quantile(0.02)
vmax = gdf_wgs["log_density"].quantile(0.98)
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

gdf_wgs.plot(
    column="log_density", ax=ax1, cmap=cmap_pur, norm=norm,
    linewidth=0.15, edgecolor="#cccccc"
)
# Division boundaries overlay
gdf_div.boundary.plot(ax=ax1, color="white", linewidth=1.5)

sm = plt.cm.ScalarMappable(cmap=cmap_pur, norm=norm)
sm.set_array([])
cb = fig.colorbar(sm, ax=ax1, fraction=0.025, pad=0.01, shrink=0.85,
                  orientation="vertical")
tick_vals = [np.log1p(v) for v in [100, 500, 1000, 3000, 8000, 20000]]
tick_labs  = ["100","500","1k","3k","8k","20k+"]
valid = [(v,l) for v,l in zip(tick_vals,tick_labs) if vmin <= v <= vmax]
if valid:
    cb.set_ticks([v for v,_ in valid])
    cb.set_ticklabels([l for _,l in valid])
cb.set_label("Pop. Density (persons/km2, log scale)", fontsize=8)

# Division name labels
label_coords = {
    "Dhaka":      (90.38, 23.75), "Chittagong": (91.75, 22.70),
    "Rajshahi":   (88.90, 24.45), "Khulna":     (89.35, 22.70),
    "Barisal":    (90.20, 22.35), "Sylhet":     (91.90, 24.45),
    "Mymensingh": (90.40, 24.80), "Rangpur":    (89.20, 25.75),
}
for div, (x, y) in label_coords.items():
    ax1.annotate(div, xy=(x, y), fontsize=7, ha="center",
                 color="white", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.15", fc="black",
                           alpha=0.45, lw=0))

ax1.set_title("(a) Upazila-Level Population Density\n(n=499 upazilas, 2022 Census, log scale)",
              fontsize=10, fontweight="bold")
ax1.set_axis_off()

# ── Panel B: Upazila density classified into 5 quintiles ─────────────────────
gdf_wgs["density"] = gdf_proj["pop_density"].values
q_labels = ["Q1 Very Low","Q2 Low","Q3 Medium","Q4 High","Q5 Very High"]
q_colors  = ["#f2f0f7","#cbc9e2","#9e9ac8","#756bb1","#54278f"]
gdf_wgs["quintile"] = pd.qcut(gdf_wgs["density"], 5, labels=q_labels)

for lbl, col in zip(q_labels, q_colors):
    gdf_wgs[gdf_wgs["quintile"] == lbl].plot(ax=ax2, color=col,
        linewidth=0.15, edgecolor="#cccccc")
gdf_div.boundary.plot(ax=ax2, color="white", linewidth=1.5)

# Annotate divisions with their top-quintile upazila share
for div, (x, y) in label_coords.items():
    subset = gdf_wgs[gdf_wgs["division"] == div]
    n_total = len(subset)
    n_high  = (subset["quintile"].isin(["Q4 High","Q5 Very High"])).sum()
    pct = n_high / n_total * 100
    ax2.annotate(f"{div}\n{pct:.0f}% high\ndensity",
                 xy=(x, y), fontsize=6.5, ha="center",
                 color="white", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.15", fc="black",
                           alpha=0.45, lw=0))

legend_patches = [mpatches.Patch(color=c, label=l)
                  for l, c in zip(q_labels, q_colors)]
ax2.legend(handles=legend_patches, fontsize=7.5, loc="lower left",
           framealpha=0.92, title="Density Quintile", title_fontsize=8)
ax2.set_title("(b) Population Density Quintile Classification\n(% = share of high-density upazilas per division)",
              fontsize=10, fontweight="bold")
ax2.set_axis_off()

# ── Panel C: Division density vs incidence horizontal bar ────────────────────
div_sorted = div_stats.sort_values("div_density", ascending=True)
x_vals   = div_sorted["div_density"].values
divnames = div_sorted["division"].values
inc_vals = div_sorted["suspected_incidence"].values

# Colour by incidence quintile
inc_norm = mcolors.Normalize(vmin=inc_vals.min(), vmax=inc_vals.max())
inc_cmap = LinearSegmentedColormap.from_list("inc", ["#fee5d9","#a50f15"])
bar_colors = [inc_cmap(inc_norm(v)) for v in inc_vals]

bars = ax3.barh(range(len(divnames)), x_vals, color=bar_colors,
                edgecolor="white", linewidth=0.5)
ax3.set_yticks(range(len(divnames)))
ax3.set_yticklabels(divnames, fontsize=10)
ax3.set_xlabel("Population Density (persons/km2)", fontsize=9)

for i, (bar, inc) in enumerate(zip(bars, inc_vals)):
    ax3.text(bar.get_width() + 8, i,
             f"{bar.get_width():.0f}/km2\n({inc:.0f}/100k incidence)",
             va="center", fontsize=7.5, color="#333333")

# Colour legend for incidence
sm2 = plt.cm.ScalarMappable(cmap=inc_cmap, norm=inc_norm)
sm2.set_array([])
cb2 = fig.colorbar(sm2, ax=ax3, fraction=0.05, pad=0.18, shrink=0.6,
                   orientation="vertical")
cb2.set_label("Suspected Incidence\nper 100,000", fontsize=8)

ax3.set_title("(c) Division-Level Density\nvs Measles Incidence",
              fontsize=10, fontweight="bold")
ax3.set_xlim(0, div_sorted["div_density"].max() * 1.55)
ax3.spines[["top","right"]].set_visible(False)
ax3.grid(axis="x", alpha=0.2)

fig.suptitle(
    "Figure 9. Upazila-Level Population Density Surface, Bangladesh 2026\n"
    "Data: Bangladesh Population and Housing Census 2022 (n=499 upazilas); "
    "area derived from UTM Zone 46N projection",
    fontsize=11, fontweight="bold", y=1.02,
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig9_upazila_density.png", dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT}/fig9_upazila_density.png")
plt.close()

div_stats.to_csv(
    "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_upazila_density_summary.csv",
    index=False,
)
