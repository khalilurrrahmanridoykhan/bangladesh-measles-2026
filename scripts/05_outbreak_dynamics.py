"""
Table 3 + supplementary: Outbreak dynamics.
- Doubling time (log-linear regression on first 14 days)
- Week-over-week growth rate
- Active cases estimate
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA = "/Users/khalilur/Documents/AIWORK"
OUT  = "/Users/khalilur/Documents/AIWORK/analysis/figures"

df = pd.read_csv(f"{DATA}/measles_national_summary.csv", parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# ── Doubling time (first 14 days) ────────────────────────────────────────────
early = df.iloc[:14].copy()
early["day"] = range(1, 15)
log_cum = np.log(early["Suspected Cases (Cumulative)"].values)
slope, intercept, r, p, se = stats.linregress(early["day"].values, log_cum)
doubling_time = round(np.log(2) / slope, 1)

# ── Week-over-week growth rate ───────────────────────────────────────────────
df["week"] = (df.index // 7) + 1
weekly = df.groupby("week").agg(
    week_start=("Date", "first"),
    week_end=("Date", "last"),
    total_suspected=("Suspected Cases (24h)", "sum"),
    total_confirmed=("Confirmed Cases (24h)", "sum"),
).reset_index()

weekly["growth_rate_pct"] = (
    (weekly["total_suspected"] - weekly["total_suspected"].shift(1))
    / weekly["total_suspected"].shift(1) * 100
).round(1)

# ── Active cases (hospitalized - recovered) ──────────────────────────────────
df["active_cases"] = df["Hospitalized (Cumulative)"] - df["Recovered (Cumulative)"]

# ── Figure: weekly totals bar + active cases line ───────────────────────────
fig, ax1 = plt.subplots(figsize=(11, 5))
ax2 = ax1.twinx()

colors = ["#E07B54" if (g is not None and not pd.isna(g) and g > 0) else "#3A6EA5"
          for g in weekly["growth_rate_pct"]]

bars = ax1.bar(weekly["week"], weekly["total_suspected"],
               color="#E07B54", alpha=0.7, label="Weekly suspected cases")
ax1.bar(weekly["week"], weekly["total_confirmed"],
        color="#3A6EA5", alpha=0.8, label="Weekly confirmed cases")

ax2.plot(df["week"], df["active_cases"], color="#2E8B57",
         linewidth=2, linestyle="-", label="Active cases (est.)")
ax2.set_ylabel("Active Cases (Hospitalized − Recovered)", fontsize=10, color="#2E8B57")
ax2.tick_params(axis="y", labelcolor="#2E8B57")

ax1.set_xlabel("Epidemiological Week", fontsize=11)
ax1.set_ylabel("Weekly Case Count", fontsize=11)
ax1.set_title("Figure S1. Weekly Measles Case Counts and Estimated Active Cases\n"
              "Bangladesh 2026", fontsize=11, fontweight="bold")
ax1.set_xticks(weekly["week"])
ax1.set_xticklabels([f"Wk {w}\n({d.strftime('%d %b')})"
                      for w, d in zip(weekly["week"], weekly["week_start"])],
                     fontsize=8)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, fontsize=9, loc="upper left")
ax1.spines[["top"]].set_visible(False)
ax1.grid(axis="y", linestyle="--", alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

fig.tight_layout()
fig.savefig(f"{OUT}/figS1_weekly_dynamics.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/figS1_weekly_dynamics.png")
plt.close()

# ── Table 3 ─────────────────────────────────────────────────────────────────
t3_summary = pd.DataFrame([
    ("Outbreak start date (tracking)", "15 March 2026"),
    ("Analysis period", f"{df['Date'].min().strftime('%d %b %Y')} – {df['Date'].max().strftime('%d %b %Y')}"),
    ("Doubling time (first 14 days)", f"{doubling_time} days (r²={r**2:.2f})"),
    ("Daily growth rate (early phase)", f"{round(slope * 100, 2)}% per day"),
    ("Peak weekly suspected cases", f"{int(weekly['total_suspected'].max()):,} (Week {int(weekly.loc[weekly['total_suspected'].idxmax(),'week'])})"),
    ("Week with highest growth rate", f"{weekly.loc[weekly['growth_rate_pct'].idxmax(),'growth_rate_pct']:.1f}% (Week {int(weekly.loc[weekly['growth_rate_pct'].idxmax(),'week'])})"),
    ("Max estimated active cases", f"{int(df['active_cases'].max()):,}"),
    ("Active cases at end of period", f"{int(df['active_cases'].iloc[-1]):,}"),
], columns=["Metric", "Value"])

t3_weekly = weekly[["week","week_start","week_end","total_suspected","total_confirmed","growth_rate_pct"]].copy()
t3_weekly.columns = ["Week","Start Date","End Date","Suspected Cases","Confirmed Cases","WoW Growth (%)"]
t3_weekly["Start Date"] = pd.to_datetime(t3_weekly["Start Date"]).dt.strftime("%d %b")
t3_weekly["End Date"]   = pd.to_datetime(t3_weekly["End Date"]).dt.strftime("%d %b")

t3_summary.to_csv(f"{DATA}/analysis/table3_dynamics_summary.csv", index=False)
t3_weekly.to_csv(f"{DATA}/analysis/table3_dynamics_weekly.csv", index=False)

print(f"\nTable 3 summary:")
print(t3_summary.to_string(index=False))
print(f"\nTable 3 weekly breakdown:")
print(t3_weekly.to_string(index=False))
