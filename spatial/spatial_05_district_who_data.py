"""
Spatial Analysis - Figure 5: District-level analysis using WHO/UNICEF data
- Panel A: All 64 districts, 4 WHO-reported districts highlighted by case count
- Panel B: Dhaka district zoomed with 6 UNICEF urban hotspot clusters annotated
- Panel C: 4 district case counts vs division totals (bar chart)
Data source: WHO Disease Outbreak News DON598 (April 14, 2026) +
             UNICEF Bangladesh Situation Report No.1 (April 8, 2026)
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import numpy as np
import warnings
warnings.filterwarnings("ignore")

SHP = "/Users/khalilur/Documents/GMGI/ewars/src/assets/data/extracted_shapefile/bd_adm3_output_shapefile.shp"
OUT = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

# ── Load shapefile ───────────────────────────────────────────────────────────
gdf = gpd.read_file(SHP)

# District-level boundaries (dissolve upazila to district)
gdf_dist = gdf.dissolve(by="district", aggfunc="sum").reset_index()[["district","geometry"]]
gdf_div  = gdf.dissolve(by="division", aggfunc="sum").reset_index()[["division","geometry"]]

# ── WHO district-level data (DON598, April 14 2026) ─────────────────────────
who_districts = pd.DataFrame({
    "district":    ["Dhaka", "Rajshahi", "Chittagong", "Khulna"],
    "cases_who":   [8263,     3747,        2514,          1568],
    "source":      ["WHO DON598"] * 4,
    "date":        ["14 Apr 2026"] * 4,
})

# Division totals at same date (April 14 from WHO)
div_totals = {
    "Dhaka": 13685, "Rajshahi": 5832, "Chittagong": 4065, "Khulna": 2337
}
who_districts["division_total"] = who_districts["district"].map(div_totals)
who_districts["district_pct"]   = (who_districts["cases_who"] /
                                    who_districts["division_total"] * 100).round(1)

# ── UNICEF urban hotspot coordinates (Dhaka city clusters) ───────────────────
dhaka_hotspots = {
    "Demra":           (90.473, 23.710),
    "Jatrabari":       (90.432, 23.713),
    "Kamrangirchar":   (90.371, 23.713),
    "Korail":          (90.413, 23.793),
    "Mirpur":          (90.367, 23.808),
    "Tejgaon":         (90.398, 23.758),
}

# ── Border hotspot districts ─────────────────────────────────────────────────
border_hotspots = {
    "Jessore":    (89.184, 23.168),   # = Jashore, Khulna division
    "Nawabganj":  (88.280, 24.596),   # = Chapainawabganj, Rajshahi division
}

# ── Merge WHO data with district geometries ──────────────────────────────────
merged = gdf_dist.merge(who_districts, on="district", how="left")
merged["highlighted"] = merged["cases_who"].notna()

# ── FIGURE ──────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 8))
ax1 = fig.add_subplot(1, 3, 1)
ax2 = fig.add_subplot(1, 3, 2)
ax3 = fig.add_subplot(1, 3, 3)

# ── Panel A: National district map ───────────────────────────────────────────
# All districts in light grey
merged[~merged["highlighted"]].plot(ax=ax1, color="#e8e8e8", edgecolor="white",
                                     linewidth=0.4)
# Division boundaries overlay
gdf_div.boundary.plot(ax=ax1, color="#888888", linewidth=0.9, linestyle="--")

# WHO-reported districts coloured by case count
cmap_red = LinearSegmentedColormap.from_list("wred", ["#fcbba1","#a50f15"])
norm = mcolors.Normalize(vmin=1000, vmax=9000)
who_merged = merged[merged["highlighted"]].copy()
who_merged.plot(column="cases_who", ax=ax1, cmap=cmap_red, norm=norm,
                edgecolor="black", linewidth=1.2)

# Border hotspot markers
for name, (lon, lat) in border_hotspots.items():
    ax1.plot(lon, lat, marker="*", color="#ff7f00", markersize=14,
             markeredgecolor="black", markeredgewidth=0.5, zorder=6)
    ax1.annotate(name, (lon, lat), xytext=(4, 4),
                 textcoords="offset points", fontsize=6.5, color="#d95f02",
                 fontweight="bold")

# WHO district labels
label_offsets = {
    "Dhaka":      (1,  3),
    "Rajshahi":   (-28, 3),
    "Chittagong": (3,  -8),
    "Khulna":     (3,  -8),
}
for _, row in who_merged.iterrows():
    cx = row.geometry.centroid.x
    cy = row.geometry.centroid.y
    dx, dy = label_offsets.get(row["district"], (3, 3))
    ax1.annotate(f"{row['district']}\n{int(row['cases_who']):,}",
                 (cx, cy), xytext=(dx, dy), textcoords="offset points",
                 fontsize=7.5, fontweight="bold", color="black",
                 bbox=dict(boxstyle="round,pad=0.25", fc="white", alpha=0.85, lw=0.5))

sm = plt.cm.ScalarMappable(cmap=cmap_red, norm=norm)
sm.set_array([])
cb = fig.colorbar(sm, ax=ax1, fraction=0.03, pad=0.02, shrink=0.7)
cb.set_label("Suspected Cases (WHO DON598\n14 April 2026)", fontsize=7.5)

legend_elems = [
    mpatches.Patch(fc="#e8e8e8", ec="grey", label="No WHO district data"),
    mpatches.Patch(fc="#fcbba1", ec="black", label="WHO-reported district"),
    Line2D([0],[0], marker="*", color="w", markerfacecolor="#ff7f00",
           markersize=10, label="Border hotspot (UNICEF)"),
]
ax1.legend(handles=legend_elems, fontsize=7, loc="lower left",
           framealpha=0.9)
ax1.set_title("(a) WHO-Reported District Case Counts\n+ Border Hotspots (UNICEF)",
              fontsize=10, fontweight="bold")
ax1.set_axis_off()

# ── Panel B: Dhaka division zoom + urban hotspot clusters ────────────────────
dhaka_upz = gdf[gdf["division"] == "Dhaka"].dissolve(by="district", aggfunc="sum").reset_index()
dhaka_upz.plot(ax=ax2, color="#fee0d2", edgecolor="#888888", linewidth=0.6)

# Highlight Dhaka district specifically
dhaka_dist = dhaka_upz[dhaka_upz["district"] == "Dhaka"]
dhaka_dist.plot(ax=ax2, color="#fc9272", edgecolor="black", linewidth=1.2)

# Plot urban hotspot clusters
colors_hs = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b"]
for (name, (lon, lat)), col in zip(dhaka_hotspots.items(), colors_hs):
    ax2.plot(lon, lat, marker="o", color=col, markersize=11,
             markeredgecolor="white", markeredgewidth=1.2, zorder=6)
    offset_x = 0.01 if lon < 90.41 else -0.005
    offset_y = 0.012 if lat < 23.76 else -0.015
    ax2.annotate(name, (lon, lat),
                 xytext=(lon + offset_x, lat + offset_y),
                 fontsize=7.5, fontweight="bold", color=col,
                 arrowprops=dict(arrowstyle="-", color=col, lw=0.8))

# District labels
for _, row in dhaka_upz.iterrows():
    cx = row.geometry.centroid.x
    cy = row.geometry.centroid.y
    ax2.annotate(row["district"], (cx, cy), fontsize=5.5,
                 ha="center", va="center", color="#444444")

ax2.set_title("(b) Dhaka Division: 8,263 Cases in Dhaka District\n6 Urban Hotspot Clusters (UNICEF)",
              fontsize=10, fontweight="bold")
ax2.set_xlim(88.9, 91.0)
ax2.set_ylim(22.8, 25.0)
ax2.set_axis_off()

# Inset legend
hotspot_legend = [Line2D([0],[0], marker="o", color="w", markerfacecolor=c,
                          markersize=8, label=n)
                  for n, c in zip(dhaka_hotspots.keys(), colors_hs)]
ax2.legend(handles=hotspot_legend, fontsize=6.5, loc="lower right",
           title="UNICEF Hotspot Clusters", title_fontsize=7, framealpha=0.9)

# ── Panel C: District cases vs division totals ────────────────────────────────
districts = who_districts["district"].tolist()
d_cases   = who_districts["cases_who"].tolist()
div_tots  = who_districts["division_total"].tolist()
x = np.arange(len(districts))
w = 0.38

bars1 = ax3.bar(x - w/2, div_tots, w, color="#4292c6", alpha=0.85,
                edgecolor="white", label="Division total (all districts)")
bars2 = ax3.bar(x + w/2, d_cases, w, color="#cb181d", alpha=0.85,
                edgecolor="white", label="District capital only (WHO)")

for bar in bars1:
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
             f"{int(bar.get_height()):,}", ha="center", va="bottom", fontsize=7.5)
for bar, pct in zip(bars2, who_districts["district_pct"]):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
             f"{int(bar.get_height()):,}\n({pct:.0f}%)", ha="center",
             va="bottom", fontsize=7, color="#67000d")

ax3.set_xticks(x)
ax3.set_xticklabels(districts, fontsize=10)
ax3.set_ylabel("Suspected Cases (as of 14 April 2026)", fontsize=9)
ax3.set_title("(c) District Capital vs Full Division Case Burden\n(% = district share of division total)",
              fontsize=10, fontweight="bold")
ax3.legend(fontsize=8, loc="upper right")
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax3.spines[["top","right"]].set_visible(False)
ax3.grid(axis="y", alpha=0.25)

fig.suptitle(
    "Figure 5. District-Level Analysis Using WHO/UNICEF Data (April 2026)\n"
    "WHO Disease Outbreak News DON598 + UNICEF Bangladesh Situation Report No.1",
    fontsize=12, fontweight="bold", y=1.02
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig5_district_who_unicef.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/fig5_district_who_unicef.png")

# ── Print WHO district table ─────────────────────────────────────────────────
print("\nTable: WHO/UNICEF District-Level Data (14 April 2026)")
print(who_districts[["district","cases_who","division_total","district_pct"]].to_string(index=False))
who_districts.to_csv(
    "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_who_district_data.csv",
    index=False
)
plt.close()
