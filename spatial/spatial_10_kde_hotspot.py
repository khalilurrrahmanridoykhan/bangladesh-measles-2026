"""
Spatial Analysis - Figure 10: Kernel Density Estimation (KDE) hotspot surface
Point data: 12 city corporation centroids + 6 UNICEF urban clusters
Weights: CC coverage * target population (proxy for outbreak intensity)
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import gaussian_kde
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings("ignore")

SHP = "/Users/khalilur/Documents/GMGI/ewars/src/assets/data/extracted_shapefile/bd_adm3_output_shapefile.shp"
OUT = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

# ── Load shapefile ─────────────────────────────────────────────────────────
gdf = gpd.read_file(SHP)
gdf_div  = gdf.dissolve(by="division").reset_index()[["division","geometry"]]
gdf_dist = gdf.dissolve(by="district").reset_index()[["district","geometry"]]

# ── City Corporation point data (DGHS, 21 June 2026) ─────────────────────
cc_data = pd.DataFrame([
    ("Barishal CC",    "Barisal",    43506,  44119, 22.701, 90.364),
    ("Chittagong CC",  "Chittagong",300285, 327177, 22.329, 91.836),
    ("Cumilla CC",     "Chittagong", 48004,  48643, 23.457, 91.182),
    ("Dhaka North CC", "Dhaka",     495884, 544333, 23.828, 90.376),
    ("Dhaka South CC", "Dhaka",     404074, 415870, 23.710, 90.406),
    ("Gazipur CC",     "Dhaka",     178423, 202587, 23.996, 90.426),
    ("Narayanganj CC", "Dhaka",      78337,  82230, 23.621, 90.498),
    ("Khulna CC",      "Khulna",     92701,  95002, 22.815, 89.568),
    ("Mymensingh CC",  "Mymensingh", 58668,  59184, 24.746, 90.408),
    ("Rajshahi CC",    "Rajshahi",   54886,  59814, 24.374, 88.601),
    ("Rangpur CC",     "Rangpur",    82249,  81461, 25.746, 89.275),
    ("Sylhet CC",      "Sylhet",     68933,  68941, 24.899, 91.872),
], columns=["cc_name","division","cc_target","cc_vaccinated","lat","lon"])

# Intensity proxy: target population (larger target = larger urban pop = more at risk)
cc_data["intensity"] = cc_data["cc_target"] / cc_data["cc_target"].max()

# ── UNICEF urban hotspot clusters (Dhaka district, April 2026) ────────────
unicef_clusters = pd.DataFrame([
    ("Demra",          90.473, 23.710),
    ("Jatrabari",      90.432, 23.713),
    ("Kamrangirchar",  90.371, 23.713),
    ("Korail",         90.413, 23.793),
    ("Mirpur",         90.367, 23.808),
    ("Tejgaon",        90.398, 23.758),
], columns=["cluster","lon","lat"])
unicef_clusters["intensity"] = 0.35   # moderate weight relative to CCs

# ── WHO district border hotspots ──────────────────────────────────────────
border_hs = pd.DataFrame([
    ("Jessore (border)",  89.184, 23.168),
    ("Nawabganj (border)",88.280, 24.596),
], columns=["name","lon","lat"])
border_hs["intensity"] = 0.15

# ── Build weighted point dataset for KDE ─────────────────────────────────
all_lons = np.concatenate([
    cc_data["lon"].values,
    unicef_clusters["lon"].values,
    border_hs["lon"].values,
])
all_lats = np.concatenate([
    cc_data["lat"].values,
    unicef_clusters["lat"].values,
    border_hs["lat"].values,
])
all_weights = np.concatenate([
    cc_data["intensity"].values,
    unicef_clusters["intensity"].values,
    border_hs["intensity"].values,
])

# Weighted KDE: repeat each point proportional to its weight
n_reps = (all_weights * 200).astype(int).clip(min=1)
lon_rep = np.repeat(all_lons, n_reps)
lat_rep = np.repeat(all_lats, n_reps)

# Grid over Bangladesh bounds
lon_min, lon_max = 88.0, 92.7
lat_min, lat_max = 20.5, 26.7
grid_res = 200
lon_grid = np.linspace(lon_min, lon_max, grid_res)
lat_grid = np.linspace(lat_min, lat_max, grid_res)
LON, LAT = np.meshgrid(lon_grid, lat_grid)

print("Fitting KDE...")
kde = gaussian_kde(np.vstack([lon_rep, lat_rep]), bw_method=0.18)
Z = kde(np.vstack([LON.ravel(), LAT.ravel()])).reshape(LON.shape)
Z_norm = Z / Z.max()

# Mask outside Bangladesh (rough bounding polygon approach: set to NaN)
from shapely.geometry import Point
from shapely.ops import unary_union
bd_union = unary_union(gdf.geometry)
mask = np.zeros(LON.shape, dtype=bool)
step = 4
for i in range(0, grid_res, step):
    for j in range(0, grid_res, step):
        if bd_union.contains(Point(lon_grid[j], lat_grid[i])):
            mask[i:i+step, j:j+step] = True

Z_masked = np.where(mask, Z_norm, np.nan)
print("KDE complete.")

# ── FIGURE 10: 2-panel ────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

# ── Panel A: KDE hotspot surface ─────────────────────────────────────────
cmap_heat = LinearSegmentedColormap.from_list("heat",
    ["#ffffcc","#ffeda0","#feb24c","#f03b20","#bd0026","#67000d"])
norm_z = mcolors.Normalize(vmin=0, vmax=1)

# Grey base map
gdf_div.plot(ax=ax1, color="#e8e8e8", edgecolor="white", linewidth=0.5)

# KDE surface
im = ax1.pcolormesh(LON, LAT, Z_masked, cmap=cmap_heat, norm=norm_z,
                    alpha=0.82, zorder=3, shading="auto")
gdf_div.boundary.plot(ax=ax1, color="#555555", linewidth=0.9, zorder=4)

cb = fig.colorbar(im, ax=ax1, fraction=0.03, pad=0.02, shrink=0.8)
cb.set_label("Normalised Transmission Intensity (KDE)", fontsize=8.5)
cb.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
cb.set_ticklabels(["Low","","Medium","","High"])

# Mark CC points
ax1.scatter(cc_data["lon"], cc_data["lat"],
            s=cc_data["cc_target"]/4000 + 50,
            c="#ffffff", edgecolors="#333333", linewidths=1.2,
            zorder=6, label="City Corporation", alpha=0.9)
# Mark UNICEF clusters
ax1.scatter(unicef_clusters["lon"], unicef_clusters["lat"],
            s=60, marker="^", c="#ffff00", edgecolors="#333333",
            linewidths=0.8, zorder=7, label="UNICEF Urban Cluster")
# Mark border hotspots
ax1.scatter(border_hs["lon"], border_hs["lat"],
            s=80, marker="*", c="#00eeff", edgecolors="#333333",
            linewidths=0.8, zorder=7, label="Border Hotspot (UNICEF)")

# Division labels
label_coords = {
    "Dhaka":      (90.38, 23.75), "Chittagong": (91.70, 22.50),
    "Rajshahi":   (88.90, 24.45), "Khulna":     (89.20, 22.60),
    "Barisal":    (90.20, 22.15), "Sylhet":     (91.85, 24.45),
    "Mymensingh": (90.40, 24.80), "Rangpur":    (89.20, 25.75),
}
for div, (x, y) in label_coords.items():
    ax1.annotate(div, xy=(x, y), fontsize=8, ha="center",
                 fontweight="bold", color="white",
                 bbox=dict(boxstyle="round,pad=0.15", fc="black",
                           alpha=0.45, lw=0))

ax1.legend(fontsize=8, loc="lower left", framealpha=0.9)
ax1.set_title("(a) Kernel Density Estimation (KDE) Transmission Hotspot Surface\n"
              "Weighted: City Corp. target pop. + UNICEF urban clusters + border hotspots",
              fontsize=10, fontweight="bold")
ax1.set_xlim(87.9, 92.8)
ax1.set_ylim(20.4, 26.8)
ax1.set_axis_off()

# ── Panel B: Dhaka zoom — KDE + UNICEF clusters ─────────────────────────
# Clip to Dhaka division
dhaka_gdf = gdf[gdf["division"] == "Dhaka"].dissolve(by="district").reset_index()
dhaka_union = unary_union(dhaka_gdf.geometry)

# Re-mask for Dhaka zoom
lon_z = np.linspace(89.8, 91.2, 250)
lat_z = np.linspace(23.0, 25.2, 250)
LON_Z, LAT_Z = np.meshgrid(lon_z, lat_z)

kde_dhaka = gaussian_kde(np.vstack([lon_rep, lat_rep]), bw_method=0.08)
Z_dhaka = kde_dhaka(np.vstack([LON_Z.ravel(), LAT_Z.ravel()])).reshape(LON_Z.shape)
Z_dhaka_norm = Z_dhaka / Z_dhaka.max()

mask_dhaka = np.zeros(LON_Z.shape, dtype=bool)
step2 = 3
for i in range(0, 250, step2):
    for j in range(0, 250, step2):
        if dhaka_union.contains(Point(lon_z[j], lat_z[i])):
            mask_dhaka[i:i+step2, j:j+step2] = True
Z_dhaka_masked = np.where(mask_dhaka, Z_dhaka_norm, np.nan)

dhaka_gdf.plot(ax=ax2, color="#e8e8e8", edgecolor="#aaaaaa", linewidth=0.6)
im2 = ax2.pcolormesh(LON_Z, LAT_Z, Z_dhaka_masked, cmap=cmap_heat,
                     norm=mcolors.Normalize(0,1), alpha=0.85, zorder=3, shading="auto")
dhaka_gdf.boundary.plot(ax=ax2, color="#555555", linewidth=0.7, zorder=4)

# UNICEF clusters
cluster_colors = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b"]
for (_, row), col in zip(unicef_clusters.iterrows(), cluster_colors):
    ax2.scatter(row["lon"], row["lat"], s=180, marker="^",
                c=col, edgecolors="white", linewidths=1.5, zorder=8)
    ax2.annotate(row["cluster"], (row["lon"], row["lat"]),
                 xytext=(0.012, 0.012), textcoords="offset points",
                 fontsize=8.5, fontweight="bold", color=col,
                 xycoords="data")

# Dhaka CC centroids
dhaka_cc = cc_data[cc_data["division"] == "Dhaka"]
ax2.scatter(dhaka_cc["lon"], dhaka_cc["lat"],
            s=dhaka_cc["cc_target"]/2500 + 80,
            c="white", edgecolors="#333333", linewidths=1.5, zorder=7)
for _, row in dhaka_cc.iterrows():
    short = row["cc_name"].replace(" CC","")
    ax2.annotate(short, (row["lon"], row["lat"]),
                 xytext=(-0.05, -0.025), textcoords="offset points",
                 fontsize=7.5, color="black", ha="center",
                 xycoords="data")

cb2 = fig.colorbar(im2, ax=ax2, fraction=0.03, pad=0.02, shrink=0.8)
cb2.set_label("KDE Intensity (normalised)", fontsize=8.5)
cb2.set_ticks([0,0.5,1.0])
cb2.set_ticklabels(["Low","Medium","High"])

legend_elems = (
    [Line2D([0],[0], marker="o", color="w", markerfacecolor="white",
             markeredgecolor="black", markersize=10,
             label="City Corporation (size=target pop.)")]
  + [Line2D([0],[0], marker="^", color="w", markerfacecolor=c,
             markersize=9, label=n)
     for n, c in zip(unicef_clusters["cluster"], cluster_colors)]
)
ax2.legend(handles=legend_elems, fontsize=7.5, loc="lower right",
           framealpha=0.9, title="Transmission Clusters", title_fontsize=8)
ax2.set_title("(b) Dhaka Division: KDE Hotspot Focus\n"
              "Six UNICEF Urban Clusters and Four City Corporations",
              fontsize=10, fontweight="bold")
ax2.set_xlim(89.8, 91.2)
ax2.set_ylim(23.0, 25.2)
ax2.set_axis_off()

fig.suptitle(
    "Figure 10. Kernel Density Estimation (KDE) Transmission Hotspot Surface\n"
    "2026 Bangladesh Measles Outbreak — Weighted by Urban Population Density and UNICEF Cluster Designations",
    fontsize=12, fontweight="bold", y=1.02,
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig10_kde_hotspot.png", dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT}/fig10_kde_hotspot.png")
plt.close()
