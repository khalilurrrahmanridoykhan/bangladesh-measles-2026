"""
Spatial Analysis - Figure 2: Geographic concentration analysis
Lorenz curve, HHI, and burden distribution chart
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

DATA = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/division_measles_complete.csv"
OUT  = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

df = pd.read_csv(DATA)
df["suspected_incidence"] = df["suspected_total"] / df["population_2022"] * 100000
df["confirmed_incidence"] = df["confirmed_total"] / df["population_2022"] * 100000
df = df.sort_values("suspected_total", ascending=False).reset_index(drop=True)

total_suspected = df["suspected_total"].sum()
total_confirmed = df["confirmed_total"].sum()
total_pop       = df["population_2022"].sum()

df["suspected_share"] = df["suspected_total"] / total_suspected * 100
df["confirmed_share"] = df["confirmed_total"] / total_confirmed * 100
df["pop_share"]       = df["population_2022"] / total_pop * 100

# ── HHI and concentration metrics ───────────────────────────────────────────
hhi_suspected = ((df["suspected_share"] / 100) ** 2).sum()
hhi_confirmed = ((df["confirmed_share"] / 100) ** 2).sum()
top2_share    = df["suspected_share"].iloc[:2].sum()
top1_share    = df["suspected_share"].iloc[0]

# ── Lorenz curve ─────────────────────────────────────────────────────────────
def lorenz(values):
    vals = np.sort(values)
    cumvals = np.cumsum(vals)
    cumvals = np.insert(cumvals, 0, 0)
    cumvals = cumvals / cumvals[-1]
    cumshare = np.linspace(0, 1, len(cumvals))
    return cumshare, cumvals

def gini(values):
    vals = np.sort(values)
    n = len(vals)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * vals) / (n * np.sum(vals))) - (n + 1) / n

gini_susp = gini(df["suspected_total"].values)
gini_conf = gini(df["confirmed_total"].values)

fig = plt.figure(figsize=(16, 6))
gs  = gridspec.GridSpec(1, 3, figure=fig, wspace=0.35)

# Panel A — Suspected case share by division (horizontal bar)
ax1 = fig.add_subplot(gs[0])
colors = ["#d7301f" if i == 0 else "#fc8d59" if i == 1 else "#fdcc8a"
          for i in range(len(df))]
bars = ax1.barh(df["division"], df["suspected_share"], color=colors, edgecolor="white")
ax1.set_xlabel("Share of National Suspected Cases (%)", fontsize=9)
ax1.set_title("(a) Suspected Case Burden\nby Division", fontsize=10, fontweight="bold")
ax1.invert_yaxis()
for bar, val in zip(bars, df["suspected_share"]):
    ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
             f"{val:.1f}%", va="center", fontsize=8)
ax1.set_xlim(0, df["suspected_share"].max() + 8)
ax1.spines[["top", "right"]].set_visible(False)
ax1.text(0.98, 0.03, f"HHI = {hhi_suspected:.3f}\nTop division = {top1_share:.1f}%",
         transform=ax1.transAxes, ha="right", va="bottom", fontsize=8,
         bbox=dict(boxstyle="round", fc="#fff5eb", alpha=0.8))

# Panel B — Incidence per 100k by division
ax2 = fig.add_subplot(gs[1])
df_sorted_inc = df.sort_values("suspected_incidence", ascending=False)
bar_colors = ["#2c7bb6" if inc == df_sorted_inc["suspected_incidence"].max()
              else "#74add1" for inc in df_sorted_inc["suspected_incidence"]]
bars2 = ax2.barh(df_sorted_inc["division"], df_sorted_inc["suspected_incidence"],
                 color=bar_colors, edgecolor="white")
ax2.set_xlabel("Suspected Incidence per 100,000 Population", fontsize=9)
ax2.set_title("(b) Incidence Rate\nper 100,000 Population", fontsize=10, fontweight="bold")
ax2.invert_yaxis()
for bar, val in zip(bars2, df_sorted_inc["suspected_incidence"]):
    ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
             f"{val:.1f}", va="center", fontsize=8)
ax2.set_xlim(0, df_sorted_inc["suspected_incidence"].max() + 20)
ax2.spines[["top", "right"]].set_visible(False)

# Panel C — Lorenz curve
ax3 = fig.add_subplot(gs[2])
xs, ys = lorenz(df["suspected_total"].values)
xc, yc = lorenz(df["confirmed_total"].values)
xp, yp = lorenz(df["population_2022"].values)

ax3.plot([0, 1], [0, 1], "k--", linewidth=1, label="Perfect equality", alpha=0.5)
ax3.plot(xp, yp, color="#74c476", linewidth=2, linestyle=":", label="Population share")
ax3.plot(xs, ys, color="#d7301f", linewidth=2.5, label=f"Suspected cases (Gini={gini_susp:.2f})")
ax3.plot(xc, yc, color="#2c7bb6", linewidth=2.5, linestyle="--",
         label=f"Confirmed cases (Gini={gini_conf:.2f})")
ax3.fill_between(xs, xs, ys, alpha=0.12, color="#d7301f")
ax3.set_xlabel("Cumulative Share of Divisions\n(ranked by cases, low to high)", fontsize=9)
ax3.set_ylabel("Cumulative Share of Cases", fontsize=9)
ax3.set_title("(c) Lorenz Curve of\nGeographic Case Concentration", fontsize=10, fontweight="bold")
ax3.legend(fontsize=8, loc="upper left")
ax3.set_xlim(0, 1); ax3.set_ylim(0, 1)
ax3.spines[["top", "right"]].set_visible(False)
ax3.grid(True, alpha=0.2)

fig.suptitle(
    "Figure 2. Geographic Concentration of the 2026 Bangladesh Measles Outbreak\n"
    "across Eight Administrative Divisions",
    fontsize=12, fontweight="bold", y=1.01
)
plt.savefig(f"{OUT}/fig2_geographic_concentration.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/fig2_geographic_concentration.png")
plt.close()

print(f"\nGeographic Concentration Metrics:")
print(f"  HHI (suspected):          {hhi_suspected:.3f}")
print(f"  HHI (confirmed):          {hhi_confirmed:.3f}")
print(f"  Gini (suspected):         {gini_susp:.3f}")
print(f"  Gini (confirmed):         {gini_conf:.3f}")
print(f"  Top 1 division share:     {top1_share:.1f}%")
print(f"  Top 2 divisions share:    {top2_share:.1f}%")
