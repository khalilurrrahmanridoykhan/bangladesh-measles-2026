"""
Spatial Analysis - Figure 4: Vaccination coverage vs incidence spatial map
Side-by-side: MR campaign coverage map + incidence map + scatter
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats
import numpy as np
import warnings
warnings.filterwarnings("ignore")

SHP  = "/Users/khalilur/Documents/GMGI/ewars/src/assets/data/extracted_shapefile/bd_adm3_output_shapefile.shp"
DATA = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/division_measles_complete.csv"
OUT  = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

gdf = gpd.read_file(SHP)
gdf_div = gdf.dissolve(by="division", aggfunc="sum").reset_index()[["division","geometry"]]

df = pd.read_csv(DATA)
df["suspected_incidence"] = df["suspected_total"] / df["population_2022"] * 100000
df["confirmed_incidence"] = df["confirmed_total"] / df["population_2022"] * 100000

merged = gdf_div.merge(df, on="division", how="left")

label_coords = {
    "Dhaka": (90.38, 23.75), "Chittagong": (91.75, 22.70),
    "Rajshahi": (88.90, 24.45), "Khulna": (89.35, 22.70),
    "Barisal": (90.20, 22.35), "Sylhet": (91.90, 24.45),
    "Mymensingh": (90.40, 24.80), "Rangpur": (89.20, 25.75),
}

fig, axes = plt.subplots(1, 3, figsize=(18, 7))

# Panel A — MR campaign coverage map
ax = axes[0]
cmap_grn = LinearSegmentedColormap.from_list("wgrn", ["#edf8e9","#006d2c"])
norm_vacc = mcolors.Normalize(vmin=95, vmax=107)
merged.plot(column="mr_coverage_pct", ax=ax, cmap=cmap_grn, norm=norm_vacc,
            linewidth=0.8, edgecolor="white")
sm = plt.cm.ScalarMappable(cmap=cmap_grn, norm=norm_vacc)
sm.set_array([])
cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02)
cb.set_label("MR Campaign Coverage (%)", fontsize=8)
for _, row in merged.iterrows():
    div = row["division"]
    if div in label_coords:
        x, y = label_coords[div]
        ax.annotate(f"{row['mr_coverage_pct']:.1f}%", xy=(x, y),
                    fontsize=7, ha="center", va="center", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7, lw=0))
ax.set_title("(a) MR Campaign 2026\nVaccination Coverage by Division",
             fontsize=10, fontweight="bold")
ax.set_axis_off()

# Panel B — Incidence map
ax = axes[1]
cmap_red = LinearSegmentedColormap.from_list("wred", ["#fff5f0","#cb181d"])
norm_inc = mcolors.Normalize(vmin=df["suspected_incidence"].min(),
                              vmax=df["suspected_incidence"].max())
merged.plot(column="suspected_incidence", ax=ax, cmap=cmap_red, norm=norm_inc,
            linewidth=0.8, edgecolor="white")
sm2 = plt.cm.ScalarMappable(cmap=cmap_red, norm=norm_inc)
sm2.set_array([])
cb2 = fig.colorbar(sm2, ax=ax, fraction=0.035, pad=0.02)
cb2.set_label("Suspected Incidence per 100,000", fontsize=8)
for _, row in merged.iterrows():
    div = row["division"]
    if div in label_coords:
        x, y = label_coords[div]
        ax.annotate(f"{row['suspected_incidence']:.0f}", xy=(x, y),
                    fontsize=7, ha="center", va="center", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7, lw=0))
ax.set_title("(b) Suspected Measles Incidence\nper 100,000 Population",
             fontsize=10, fontweight="bold")
ax.set_axis_off()

# Panel C — Scatter: coverage vs incidence
ax = axes[2]
x = df["mr_coverage_pct"].values
y = df["suspected_incidence"].values
r, p = stats.pearsonr(x, y)

ax.scatter(x, y, s=120, color="#2c7bb6", edgecolor="navy", zorder=5, alpha=0.85)
for _, row in df.iterrows():
    ax.annotate(row["division"],
                (row["mr_coverage_pct"], row["suspected_incidence"]),
                textcoords="offset points", xytext=(6, 3), fontsize=8)

# Regression line
m, b, *_ = stats.linregress(x, y)
xs = np.linspace(x.min() - 0.5, x.max() + 0.5, 100)
ax.plot(xs, m * xs + b, "r--", linewidth=1.5, alpha=0.7)

ax.set_xlabel("MR Campaign 2026 Coverage (%)", fontsize=10)
ax.set_ylabel("Suspected Incidence per 100,000", fontsize=10)
ax.set_title(f"(c) Vaccination Coverage vs Incidence\n(Pearson r = {r:.3f}, p = {p:.3f})",
             fontsize=10, fontweight="bold")
ax.spines[["top","right"]].set_visible(False)
ax.grid(True, alpha=0.2)
p_str = f"p = {p:.3f}" if p >= 0.001 else "p < 0.001"
ax.text(0.97, 0.97, f"r = {r:.3f}\n{p_str}", transform=ax.transAxes,
        ha="right", va="top", fontsize=10,
        bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.8))

fig.suptitle(
    "Figure 4. Spatial Relationship Between MR Vaccination Coverage and Measles Incidence\n"
    "by Administrative Division, Bangladesh 2026",
    fontsize=12, fontweight="bold", y=1.02
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig4_vaccination_spatial.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/fig4_vaccination_spatial.png")
print(f"\nPearson r = {r:.3f}, p = {p:.3f}")
plt.close()
