"""
Spatial Analysis - Figure 6: City Corporation vaccination analysis
Multi-scale analysis: Division level + City Corporation level
Data: DGHS PDF June 21, 2026 (page 3 - city corporation vaccination)
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

SHP  = "/Users/khalilur/Documents/GMGI/ewars/src/assets/data/extracted_shapefile/bd_adm3_output_shapefile.shp"
DATA = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/division_measles_complete.csv"
OUT  = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

# ── City Corporation data (DGHS PDF, 21 June 2026, page 3) ───────────────────
cc_data = pd.DataFrame([
    ("Barishal CC",     "Barisal",     43506,   44119,  22.701, 90.364),
    ("Chittagong CC",   "Chittagong", 300285,  327177,  22.329, 91.836),
    ("Cumilla CC",      "Chittagong",  48004,   48643,  23.457, 91.182),
    ("Dhaka North CC",  "Dhaka",      495884,  544333,  23.828, 90.376),
    ("Dhaka South CC",  "Dhaka",      404074,  415870,  23.710, 90.406),
    ("Gazipur CC",      "Dhaka",      178423,  202587,  23.996, 90.426),
    ("Narayanganj CC",  "Dhaka",       78337,   82230,  23.621, 90.498),
    ("Khulna CC",       "Khulna",      92701,   95002,  22.815, 89.568),
    ("Mymensingh CC",   "Mymensingh",  58668,   59184,  24.746, 90.408),
    ("Rajshahi CC",     "Rajshahi",    54886,   59814,  24.374, 88.601),
    ("Rangpur CC",      "Rangpur",     82249,   81461,  25.746, 89.275),
    ("Sylhet CC",       "Sylhet",      68933,   68941,  24.899, 91.872),
], columns=["cc_name","division","cc_target","cc_vaccinated","lat","lon"])

cc_data["cc_coverage"] = (cc_data["cc_vaccinated"] / cc_data["cc_target"] * 100).round(1)

# ── Division vaccination data (same PDF, page 2) ─────────────────────────────
div_vacc = pd.DataFrame([
    ("Barisal",     1063638,  1070352),
    ("Chittagong",  4296218,  4449637),
    ("Dhaka",       4449632,  4591460),
    ("Khulna",      1614273,  1631314),
    ("Mymensingh",  1330655,  1352671),
    ("Rajshahi",    2048435,  2116469),
    ("Rangpur",     1888247,  1945245),
    ("Sylhet",      1323966,  1316194),
], columns=["division","div_target","div_vaccinated"])
div_vacc["div_coverage"] = (div_vacc["div_vaccinated"] / div_vacc["div_target"] * 100).round(1)

# ── Urban-Rural gap calculation ──────────────────────────────────────────────
cc_by_div = cc_data.groupby("division").agg(
    urban_target=("cc_target","sum"),
    urban_vaccinated=("cc_vaccinated","sum")
).reset_index()

div_merged = div_vacc.merge(cc_by_div, on="division", how="left")
div_merged["urban_coverage"]  = (div_merged["urban_vaccinated"] /
                                  div_merged["urban_target"] * 100).round(1)
div_merged["rural_target"]    = div_merged["div_target"] - div_merged["urban_target"]
div_merged["rural_vaccinated"]= div_merged["div_vaccinated"] - div_merged["urban_vaccinated"]
div_merged["rural_coverage"]  = (div_merged["rural_vaccinated"] /
                                  div_merged["rural_target"] * 100).round(1)
div_merged["urban_rural_gap"] = (div_merged["urban_coverage"] -
                                  div_merged["rural_coverage"]).round(1)

# Merge with case data
case_df = pd.read_csv(DATA)
case_df["suspected_incidence"] = case_df["suspected_total"] / case_df["population_2022"] * 100000
div_full = div_merged.merge(
    case_df[["division","suspected_incidence","suspected_total"]],
    on="division", how="left"
)

print("Urban-Rural Vaccination Gap by Division:")
print(div_full[["division","urban_coverage","rural_coverage",
                "urban_rural_gap","suspected_incidence"]].to_string(index=False))

# ── Load shapefile ───────────────────────────────────────────────────────────
gdf = gpd.read_file(SHP)
gdf_div = gdf.dissolve(by="division", aggfunc="sum").reset_index()[["division","geometry"]]
merged_shp = gdf_div.merge(div_full, on="division", how="left")

# ── FIGURE ──────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 7))
ax1 = fig.add_subplot(1, 3, 1)
ax2 = fig.add_subplot(1, 3, 2)
ax3 = fig.add_subplot(1, 3, 3)

# ── Panel A: Map of 12 CC vaccination coverage ──────────────────────────────
merged_shp.plot(ax=ax1, color="#e8e8e8", edgecolor="#aaaaaa", linewidth=0.5)
gdf_div.boundary.plot(ax=ax1, color="#555555", linewidth=1.0)

cmap_cc = LinearSegmentedColormap.from_list("cc", ["#d73027","#fee090","#91cf60","#1a9850"])
norm_cc = mcolors.Normalize(vmin=98, vmax=116)

sc = ax1.scatter(
    cc_data["lon"], cc_data["lat"],
    c=cc_data["cc_coverage"],
    cmap=cmap_cc, norm=norm_cc,
    s=cc_data["cc_target"] / 5000 + 80,
    edgecolors="white", linewidths=1.2, zorder=5, alpha=0.9
)

label_offsets = {
    "Barishal CC":    ( 0.02, -0.25), "Chittagong CC":  ( 0.10, -0.20),
    "Cumilla CC":     ( 0.15,  0.10), "Dhaka North CC": (-0.35,  0.18),
    "Dhaka South CC": ( 0.12, -0.18), "Gazipur CC":     ( 0.12,  0.10),
    "Narayanganj CC": ( 0.12, -0.12), "Khulna CC":      (-0.45,  0.05),
    "Mymensingh CC":  ( 0.12,  0.10), "Rajshahi CC":    (-0.45,  0.10),
    "Rangpur CC":     ( 0.12,  0.10), "Sylhet CC":      ( 0.10,  0.12),
}
for _, row in cc_data.iterrows():
    dx, dy = label_offsets.get(row["cc_name"], (0.1, 0.1))
    short  = row["cc_name"].replace(" CC","")
    color  = "#d73027" if row["cc_coverage"] < 100 else "black"
    ax1.annotate(
        f"{short}\n{row['cc_coverage']:.0f}%",
        (row["lon"], row["lat"]),
        xytext=(row["lon"] + dx, row["lat"] + dy),
        fontsize=6.5, fontweight="bold", color=color,
        arrowprops=dict(arrowstyle="-", color="#888888", lw=0.6),
        bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.75, lw=0)
    )

cb = fig.colorbar(sc, ax=ax1, fraction=0.03, pad=0.02, shrink=0.75)
cb.set_label("MR Campaign Coverage (%)", fontsize=8)
ax1.set_title("(a) City Corporation-Level\nMR Vaccination Coverage\n(bubble size = target population)",
              fontsize=9, fontweight="bold")
ax1.set_axis_off()

# ── Panel B: Urban vs Rural coverage gap ─────────────────────────────────────
df_b = div_full.sort_values("urban_rural_gap", ascending=True)
x    = np.arange(len(df_b))
w    = 0.3

bars_u = ax2.barh(x + w/2, df_b["urban_coverage"], w,
                  color="#2171b5", alpha=0.85, label="Urban (City Corp)")
bars_r = ax2.barh(x - w/2, df_b["rural_coverage"], w,
                  color="#74c476", alpha=0.85, label="Rural (non-CC areas)")

ax2.axvline(100, color="red", linewidth=1.2, linestyle="--", alpha=0.7,
            label="100% target")

for i, (_, row) in enumerate(df_b.iterrows()):
    gap = row["urban_rural_gap"]
    col = "#d62728" if gap < 0 else "#2171b5"
    ax2.text(max(row["urban_coverage"], row["rural_coverage"]) + 0.2,
             i, f"gap: {gap:+.1f}pp",
             va="center", fontsize=7.5, color=col, fontweight="bold")

ax2.set_yticks(x)
ax2.set_yticklabels(df_b["division"], fontsize=9)
ax2.set_xlabel("MR Campaign Coverage (%)", fontsize=9)
ax2.set_title("(b) Urban vs Rural Vaccination Coverage\nby Division (pp = percentage points)",
              fontsize=9, fontweight="bold")
ax2.set_xlim(96, 118)
ax2.legend(fontsize=8, loc="lower right")
ax2.spines[["top","right"]].set_visible(False)
ax2.grid(axis="x", alpha=0.2)

# ── Panel C: Urban-rural gap vs division incidence ───────────────────────────
x_gap  = div_full["urban_rural_gap"].values
y_inc  = div_full["suspected_incidence"].values
r, p   = stats.pearsonr(x_gap, y_inc)
m, b, *_ = stats.linregress(x_gap, y_inc)
xs     = np.linspace(x_gap.min() - 1, x_gap.max() + 1, 100)

ax3.scatter(x_gap, y_inc, s=120, c="#d62728", edgecolors="black",
            linewidths=0.8, zorder=5, alpha=0.85)
ax3.plot(xs, m * xs + b, "b--", linewidth=1.5, alpha=0.6)

for _, row in div_full.iterrows():
    ax3.annotate(row["division"],
                 (row["urban_rural_gap"], row["suspected_incidence"]),
                 xytext=(4, 4), textcoords="offset points", fontsize=8)

ax3.set_xlabel("Urban-Rural Vaccination Gap (percentage points)", fontsize=9)
ax3.set_ylabel("Suspected Incidence per 100,000", fontsize=9)
ax3.set_title(f"(c) Urban-Rural Coverage Gap vs Disease Incidence\n(Pearson r = {r:.3f}, p = {p:.3f})",
              fontsize=9, fontweight="bold")
ax3.axvline(0, color="grey", linewidth=0.8, linestyle=":", alpha=0.6)
p_str = f"p = {p:.3f}" if p >= 0.001 else "p < 0.001"
ax3.text(0.97, 0.97, f"r = {r:.3f}\n{p_str}", transform=ax3.transAxes,
         ha="right", va="top", fontsize=10,
         bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.9))
ax3.spines[["top","right"]].set_visible(False)
ax3.grid(alpha=0.2)

fig.suptitle(
    "Figure 6. Multi-Scale Vaccination Analysis: City Corporation and Division Level\n"
    "MR Campaign 2026 — Urban-Rural Coverage Disparity and Relationship with Measles Incidence",
    fontsize=12, fontweight="bold", y=1.02
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig6_city_corporation_analysis.png", dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT}/fig6_city_corporation_analysis.png")
print(f"Pearson r (urban-rural gap vs incidence) = {r:.3f}, p = {p:.3f}")

div_full.to_csv(
    "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_urban_rural_vaccination.csv",
    index=False
)
plt.close()
