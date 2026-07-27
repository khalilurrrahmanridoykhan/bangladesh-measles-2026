"""
Spatial Analysis - Figure 8: Spatial Statistics
- Population density choropleth (from shapefile area + population)
- Bivariate spatial classification: density x incidence
- Moran's I spatial autocorrelation (n=8, Queen contiguity)
- Distance-decay from Dhaka epicenter
- OLS regression: incidence ~ density + vaccination + distance
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats
import libpysal
from esda.moran import Moran
import warnings
warnings.filterwarnings("ignore")

SHP  = "/Users/khalilur/Documents/GMGI/ewars/src/assets/data/extracted_shapefile/bd_adm3_output_shapefile.shp"
DATA = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/division_measles_complete.csv"
OUT  = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

LABEL_COORDS = {
    "Dhaka":      (90.38, 23.75), "Chittagong": (91.75, 22.70),
    "Rajshahi":   (88.90, 24.45), "Khulna":     (89.35, 22.70),
    "Barisal":    (90.20, 22.35), "Sylhet":     (91.90, 24.45),
    "Mymensingh": (90.40, 24.80), "Rangpur":    (89.20, 25.75),
}

# ── Load and project shapefile for area calculation ──────────────────────────
gdf = gpd.read_file(SHP)
gdf_proj = gdf.to_crs("EPSG:32646")             # UTM Zone 46N (Bangladesh)
gdf_proj["area_km2"] = gdf_proj.geometry.area / 1e6

gdf_div_proj = gdf_proj.dissolve(by="division", aggfunc={
    "2022": "sum",
    "area_km2": "sum",
}).reset_index()
gdf_div_proj["pop_density"] = gdf_div_proj["2022"] / gdf_div_proj["area_km2"]

gdf_div = gdf_div_proj.to_crs("EPSG:4326")[["division","geometry","pop_density","area_km2"]]

# ── Merge with case data ─────────────────────────────────────────────────────
case_df = pd.read_csv(DATA)
case_df["suspected_incidence"] = case_df["suspected_total"] / case_df["population_2022"] * 100000
merged = gdf_div.merge(case_df, on="division", how="left")

# Distance from Dhaka centroid (epicenter)
dhaka_geom = merged[merged["division"] == "Dhaka"].geometry.values[0]
dhaka_centroid = dhaka_geom.centroid
merged["dist_dhaka_km"] = merged.geometry.centroid.apply(
    lambda pt: pt.distance(dhaka_centroid) * 111.0   # degrees to km
)

print("Division Statistics:")
cols_show = ["division","pop_density","area_km2","dist_dhaka_km","suspected_incidence"]
print(merged[cols_show].round(1).to_string(index=False))

# ── Spatial Weights (Queen contiguity) ───────────────────────────────────────
merged_reset = merged.reset_index(drop=True)
w = libpysal.weights.Queen.from_dataframe(merged_reset)
w.transform = "r"

# Global Moran's I on suspected incidence (aligned to w.id_order)
incidence_arr = merged_reset["suspected_incidence"].values
mi = Moran(incidence_arr, w)
print(f"\nGlobal Moran's I = {mi.I:.4f}, p = {mi.p_sim:.4f} (999 permutations, n=8)")
print(f"Moran's I z-score = {mi.z_norm:.3f}")

# ── OLS Regression: incidence ~ density + vaccination + distance ─────────────
X_raw = merged[["pop_density", "mr_coverage_pct", "dist_dhaka_km"]].values
X_std = (X_raw - X_raw.mean(axis=0)) / X_raw.std(axis=0)
X_sm  = np.column_stack([np.ones(len(X_std)), X_std])  # placeholder, overwritten below
y     = merged["suspected_incidence"].values
X_sm  = np.column_stack([np.ones(len(X_std)), X_std])
# OLS via numpy least squares
betas, residuals_sq, rank, sv = np.linalg.lstsq(X_sm, y, rcond=None)
y_hat = X_sm @ betas
ss_res = np.sum((y - y_hat)**2)
ss_tot = np.sum((y - y.mean())**2)
r2     = 1 - ss_res / ss_tot
n, k   = len(y), X_sm.shape[1]
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k)
mse    = ss_res / (n - k)
var_b  = mse * np.linalg.inv(X_sm.T @ X_sm).diagonal()
se_b   = np.sqrt(var_b)
t_vals = betas / se_b
from scipy.stats import t as t_dist
p_vals = 2 * t_dist.sf(np.abs(t_vals), df=n - k)

# Build a simple result holder for reuse
class OLSResult:
    pass
ols = OLSResult()
ols.params       = betas
ols.bse          = se_b
ols.tvalues      = t_vals
ols.pvalues      = p_vals
ols.rsquared     = r2
ols.rsquared_adj = adj_r2

print("\nOLS Regression (standardized predictors):")
print(f"  R2 = {r2:.3f}, adj-R2 = {adj_r2:.3f}")
for name, coef, pval in zip(
    ["Intercept","Pop Density","MR Coverage","Dist Dhaka"],
    betas, p_vals
):
    print(f"  {name:16s} beta={coef:+.2f}  p={pval:.3f}")

# ── Bivariate quadrant classification ───────────────────────────────────────
density_mean   = merged["pop_density"].mean()
incidence_mean = merged["suspected_incidence"].mean()

QUAD_LABELS = {
    "HH": "HH (High Density,\nHigh Incidence)",
    "LH": "LH (Low Density,\nHigh Incidence)",
    "HL": "HL (High Density,\nLow Incidence)",
    "LL": "LL (Low Density,\nLow Incidence)",
}
QUAD_COLORS = {
    "HH": "#d73027",
    "LH": "#fdae61",
    "HL": "#74add1",
    "LL": "#e8e8e8",
}

def classify_bivar(row):
    hi_den = row["pop_density"]          > density_mean
    hi_inc = row["suspected_incidence"]  > incidence_mean
    if   hi_den and     hi_inc: return "HH"
    elif not hi_den and hi_inc: return "LH"
    elif hi_den and not hi_inc: return "HL"
    else:                       return "LL"

merged["quad"] = merged.apply(classify_bivar, axis=1)

# ── FIGURE 8: 2x2 layout ─────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
ax1, ax2 = axes[0]
ax3, ax4 = axes[1]

# Panel A: Population density map
cmap_pur = LinearSegmentedColormap.from_list("pur", ["#f2f0f7","#54278f"])
norm_den = mcolors.Normalize(vmin=merged["pop_density"].min(),
                              vmax=merged["pop_density"].max())
merged.plot(column="pop_density", ax=ax1, cmap=cmap_pur, norm=norm_den,
            linewidth=0.8, edgecolor="white")
sm = plt.cm.ScalarMappable(cmap=cmap_pur, norm=norm_den)
sm.set_array([])
cb = fig.colorbar(sm, ax=ax1, fraction=0.032, pad=0.02, shrink=0.8)
cb.set_label("Population per km2", fontsize=8)
for _, row in merged.iterrows():
    div = row["division"]
    if div in LABEL_COORDS:
        x, y = LABEL_COORDS[div]
        ax1.annotate(f"{div}\n{row['pop_density']:.0f}/km2",
                     xy=(x, y), fontsize=6.5, ha="center", fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.75, lw=0))
ax1.set_title("(a) Population Density by Administrative Division\n(persons per km2, UTM-derived area)",
              fontsize=10, fontweight="bold")
ax1.set_axis_off()

# Panel B: Bivariate choropleth
for quad_key, color in QUAD_COLORS.items():
    subset = merged[merged["quad"] == quad_key]
    if not subset.empty:
        subset.plot(ax=ax2, color=color, edgecolor="white", linewidth=0.8)
for _, row in merged.iterrows():
    div = row["division"]
    if div in LABEL_COORDS:
        x, y = LABEL_COORDS[div]
        ax2.annotate(div, xy=(x, y), fontsize=7.5, ha="center", fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.75, lw=0))
legend_patches = [mpatches.Patch(color=QUAD_COLORS[k], label=QUAD_LABELS[k].replace("\n", " "))
                  for k in ["HH","LH","HL","LL"]]
ax2.legend(handles=legend_patches, fontsize=8, loc="lower left",
           framealpha=0.9, title="Density x Incidence Class", title_fontsize=8)
ax2.set_title("(b) Bivariate Spatial Classification\nPopulation Density x Measles Incidence",
              fontsize=10, fontweight="bold")
ax2.set_axis_off()

# Panel C: Population density vs incidence + Moran's I annotation
x_den = merged["pop_density"].values
y_inc = merged["suspected_incidence"].values
r_den, p_den = stats.pearsonr(x_den, y_inc)
m_den, b_den, *_ = stats.linregress(x_den, y_inc)
xs_den = np.linspace(x_den.min() - 50, x_den.max() + 50, 100)

ax3.scatter(x_den, y_inc, s=130, c="#54278f", edgecolors="black",
            linewidths=0.8, zorder=5, alpha=0.85)
ax3.plot(xs_den, m_den * xs_den + b_den, "--", color="#54278f",
         linewidth=1.5, alpha=0.6)
for _, row in merged.iterrows():
    ax3.annotate(row["division"],
                 (row["pop_density"], row["suspected_incidence"]),
                 xytext=(4, 4), textcoords="offset points", fontsize=8)

p_str_den = f"p = {p_den:.3f}" if p_den >= 0.001 else "p < 0.001"
p_moran   = f"p = {mi.p_sim:.3f}" if mi.p_sim >= 0.001 else "p < 0.001"
ax3.text(0.97, 0.97,
         f"Pearson r = {r_den:.3f}\n{p_str_den}\n\nGlobal Moran's I = {mi.I:.3f}\n{p_moran}\n(n=8, cautionary)",
         transform=ax3.transAxes, ha="right", va="top", fontsize=9,
         bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.9))
ax3.set_xlabel("Population Density (persons per km2)", fontsize=10)
ax3.set_ylabel("Suspected Incidence per 100,000", fontsize=10)
ax3.set_title("(c) Population Density vs Measles Incidence\n(with Global Moran's I, Queen contiguity, n=8)",
              fontsize=10, fontweight="bold")
ax3.spines[["top","right"]].set_visible(False)
ax3.grid(alpha=0.2)

# Panel D: Distance from Dhaka vs incidence
x_dist = merged["dist_dhaka_km"].values
r_dist, p_dist = stats.pearsonr(x_dist, y_inc)
m_dist, b_dist, *_ = stats.linregress(x_dist, y_inc)
xs_dist = np.linspace(0, x_dist.max() + 20, 100)

ax4.scatter(x_dist, y_inc, s=130, c="#d62728", edgecolors="black",
            linewidths=0.8, zorder=5, alpha=0.85)
ax4.plot(xs_dist, m_dist * xs_dist + b_dist, "r--", linewidth=1.5, alpha=0.6)
for _, row in merged.iterrows():
    ax4.annotate(row["division"],
                 (row["dist_dhaka_km"], row["suspected_incidence"]),
                 xytext=(4, 4), textcoords="offset points", fontsize=8)

p_str_dist = f"p = {p_dist:.3f}" if p_dist >= 0.001 else "p < 0.001"
ax4.text(0.97, 0.97,
         f"Pearson r = {r_dist:.3f}\n{p_str_dist}\n\nOLS R2 = {ols.rsquared:.3f}\n(3 predictors)",
         transform=ax4.transAxes, ha="right", va="top", fontsize=9,
         bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.9))
ax4.set_xlabel("Distance from Dhaka Division Centroid (km)", fontsize=10)
ax4.set_ylabel("Suspected Incidence per 100,000", fontsize=10)
ax4.set_title("(d) Distance-Decay from Dhaka Epicenter\n(OLS: incidence ~ density + vaccination + distance)",
              fontsize=10, fontweight="bold")
ax4.spines[["top","right"]].set_visible(False)
ax4.grid(alpha=0.2)

fig.suptitle(
    "Figure 8. Spatial Autocorrelation, Population Density, and Distance-Decay Analysis\n"
    "2026 Bangladesh Measles Outbreak by Administrative Division (n=8)",
    fontsize=12, fontweight="bold", y=1.01,
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig8_spatial_stats.png", dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT}/fig8_spatial_stats.png")
plt.close()

# ── Save OLS results table ────────────────────────────────────────────────────
reg_df = pd.DataFrame({
    "Variable":    ["Intercept","Population Density (std)","MR Coverage (std)","Distance from Dhaka (std)"],
    "Beta":        ols.params.round(2),
    "SE":          ols.bse.round(2),
    "t":           ols.tvalues.round(3),
    "p-value":     ols.pvalues.round(3),
    "R2":          [round(ols.rsquared, 3)] + [None]*3,
    "adj-R2":      [round(ols.rsquared_adj, 3)] + [None]*3,
})
reg_df.to_csv(
    "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_ols_regression.csv",
    index=False,
)
print("OLS table saved.")

# ── Save population density table ────────────────────────────────────────────
density_out = merged[["division","pop_density","area_km2","dist_dhaka_km",
                       "suspected_incidence","quad"]].copy()
density_out.columns = ["Division","Pop Density/km2","Area km2","Dist Dhaka km",
                        "Suspected/100k","Bivariate Class"]
density_out = density_out.round(1)
density_out.to_csv(
    "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_population_density.csv",
    index=False,
)
print("Population density table saved.")
