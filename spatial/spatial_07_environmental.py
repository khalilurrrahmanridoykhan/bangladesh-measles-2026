"""
Spatial Analysis - Figure 7: Environmental Covariates and Measles Incidence
NASA POWER API: Temperature, Relative Humidity, Precipitation
Outbreak period: 15 March - 2 June 2026 (80 days)
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

SHP  = "/Users/khalilur/Documents/GMGI/ewars/src/assets/data/extracted_shapefile/bd_adm3_output_shapefile.shp"
DATA = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/division_measles_complete.csv"
OUT  = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

# Geographic centroids for each administrative division
DIVISION_CENTROIDS = {
    "Dhaka":      {"lat": 23.75, "lon": 90.38},
    "Chittagong": {"lat": 22.70, "lon": 91.75},
    "Rajshahi":   {"lat": 24.45, "lon": 88.90},
    "Khulna":     {"lat": 22.70, "lon": 89.35},
    "Barisal":    {"lat": 22.35, "lon": 90.20},
    "Sylhet":     {"lat": 24.45, "lon": 91.90},
    "Mymensingh": {"lat": 24.80, "lon": 90.40},
    "Rangpur":    {"lat": 25.75, "lon": 89.20},
}

def fetch_nasa_power(lat, lon, start="20260315", end="20260602"):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,RH2M,PRECTOTCORR",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    param = r.json()["properties"]["parameter"]
    t2m  = np.array(list(param["T2M"].values()))
    rh2m = np.array(list(param["RH2M"].values()))
    prec = np.array(list(param["PRECTOTCORR"].values()))
    # Replace fill values (-999)
    t2m[t2m < -900]  = np.nan
    rh2m[rh2m < -900] = np.nan
    prec[prec < -900] = np.nan
    return {
        "mean_temp":   np.nanmean(t2m),
        "max_temp":    np.nanmax(t2m),
        "mean_rh":     np.nanmean(rh2m),
        "mean_precip": np.nanmean(prec),
        "total_precip": np.nansum(prec),
    }

# ── Fetch environmental data for all 8 divisions ────────────────────────────
env_rows = []
for div, coords in DIVISION_CENTROIDS.items():
    print(f"Fetching NASA POWER for {div}...", end=" ")
    env = fetch_nasa_power(coords["lat"], coords["lon"])
    env["division"] = div
    env_rows.append(env)
    print(f"T={env['mean_temp']:.1f}C  RH={env['mean_rh']:.1f}%  P={env['mean_precip']:.2f}mm/d")

env_df = pd.DataFrame(env_rows)

# ── Merge with case data ────────────────────────────────────────────────────
case_df = pd.read_csv(DATA)
case_df["suspected_incidence"] = case_df["suspected_total"] / case_df["population_2022"] * 100000
merged = case_df.merge(env_df, on="division", how="left")

print("\nEnvironmental Covariate Summary:")
cols = ["division", "suspected_incidence", "mean_temp", "mean_rh", "mean_precip"]
print(merged[cols].round(2).to_string(index=False))

merged.to_csv(
    "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_environmental_covariates.csv",
    index=False,
)

# ── FIGURE 7: 4-panel environmental analysis ─────────────────────────────────
fig = plt.figure(figsize=(20, 9))
gs = fig.add_gridspec(1, 4, wspace=0.38)

ax_map = fig.add_subplot(gs[0])
ax_t   = fig.add_subplot(gs[1])
ax_rh  = fig.add_subplot(gs[2])
ax_pr  = fig.add_subplot(gs[3])

# ── Panel A: Environmental Gradient Map ─────────────────────────────────────
gdf = gpd.read_file(SHP)
gdf_div = gdf.dissolve(by="division", aggfunc="sum").reset_index()[["division","geometry"]]
geo_merged = gdf_div.merge(merged, on="division", how="left")

cmap_temp = LinearSegmentedColormap.from_list("temp", ["#ffffb2","#fd8d3c","#bd0026"])
norm_temp = mcolors.Normalize(vmin=merged["mean_temp"].min(), vmax=merged["mean_temp"].max())
geo_merged.plot(column="mean_temp", ax=ax_map, cmap=cmap_temp, norm=norm_temp,
                linewidth=0.8, edgecolor="white")
sm = plt.cm.ScalarMappable(cmap=cmap_temp, norm=norm_temp)
sm.set_array([])
cb = fig.colorbar(sm, ax=ax_map, fraction=0.03, pad=0.02, shrink=0.8)
cb.set_label("Mean Temp (degC)", fontsize=8)

label_coords = {
    "Dhaka": (90.38, 23.75), "Chittagong": (91.75, 22.70),
    "Rajshahi": (88.90, 24.45), "Khulna": (89.35, 22.70),
    "Barisal": (90.20, 22.35), "Sylhet": (91.90, 24.45),
    "Mymensingh": (90.40, 24.80), "Rangpur": (89.20, 25.75),
}
for _, row in geo_merged.iterrows():
    div = row["division"]
    if div in label_coords:
        x, y = label_coords[div]
        ax_map.annotate(f"{div[:4]}\n{row['mean_temp']:.1f}C",
                        xy=(x, y), fontsize=6.5, ha="center", fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.75, lw=0))
ax_map.set_title("(a) Mean Temperature\nGradient by Division\n(Mar-Jun 2026)",
                 fontsize=9, fontweight="bold")
ax_map.set_axis_off()

# ── Panel B: Temperature vs Incidence ────────────────────────────────────────
def scatter_env(ax, xvar, xlabel, color, panel_letter, data=merged):
    x = data[xvar].values
    y = data["suspected_incidence"].values
    r, p = stats.pearsonr(x, y)
    m, b, *_ = stats.linregress(x, y)
    xs = np.linspace(x.min() - 0.5, x.max() + 0.5, 100)
    ax.scatter(x, y, s=130, c=color, edgecolors="black",
               linewidths=0.8, zorder=5, alpha=0.85)
    ax.plot(xs, m*xs+b, "--", color=color, linewidth=1.5, alpha=0.55)
    for _, row in data.iterrows():
        ax.annotate(row["division"][:5], (row[xvar], row["suspected_incidence"]),
                    xytext=(4, 4), textcoords="offset points", fontsize=7.5)
    p_str = f"p = {p:.3f}" if p >= 0.001 else "p < 0.001"
    ax.text(0.97, 0.97, f"r = {r:.3f}\n{p_str}",
            transform=ax.transAxes, ha="right", va="top", fontsize=10,
            bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.9))
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel("Suspected Incidence\nper 100,000", fontsize=9)
    ax.spines[["top","right"]].set_visible(False)
    ax.grid(alpha=0.2)
    return r, p

r_t,  p_t  = scatter_env(ax_t,  "mean_temp",   "Mean Temperature (degC)",         "#d62728", "b")
ax_t.set_title(f"(b) Mean Temperature\nvs Measles Incidence", fontsize=9, fontweight="bold")

r_rh, p_rh = scatter_env(ax_rh, "mean_rh",    "Mean Relative Humidity (%)",       "#2171b5", "c")
ax_rh.set_title(f"(c) Relative Humidity\nvs Measles Incidence", fontsize=9, fontweight="bold")

r_pr, p_pr = scatter_env(ax_pr, "mean_precip","Mean Daily Precipitation (mm/day)", "#2ca02c", "d")
ax_pr.set_title(f"(d) Daily Precipitation\nvs Measles Incidence", fontsize=9, fontweight="bold")

fig.suptitle(
    "Figure 7. Environmental Covariates and Measles Incidence During the 2026 Bangladesh Outbreak\n"
    "Data Source: NASA POWER Climatology Resource (15 March - 2 June 2026); n = 8 administrative divisions",
    fontsize=11, fontweight="bold", y=1.02,
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig7_environmental_covariates.png", dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT}/fig7_environmental_covariates.png")
print(f"Pearson r: Temp={r_t:.3f}(p={p_t:.3f}), RH={r_rh:.3f}(p={p_rh:.3f}), Precip={r_pr:.3f}(p={p_pr:.3f})")
plt.close()
