"""
Figure 2: Cumulative case trajectory + Table 1 summary statistics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA = "/Users/khalilur/Documents/AIWORK"
OUT  = "/Users/khalilur/Documents/AIWORK/analysis/figures"

df = pd.read_csv(f"{DATA}/measles_national_summary.csv", parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# ── Figure 2 ────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5.5))

lines = [
    ("Suspected Cases (Cumulative)",   "#E07B54", "-",  2.2, "Suspected cases"),
    ("Confirmed Cases (Cumulative)",   "#3A6EA5", "-",  2.0, "Confirmed cases"),
    ("Hospitalized (Cumulative)",      "#6B8E6B", "--", 1.8, "Hospitalized"),
    ("Recovered (Cumulative)",         "#2E8B57", "-.", 1.8, "Recovered"),
]

for col, color, ls, lw, label in lines:
    ax.plot(df["Date"], df[col], color=color, linestyle=ls,
            linewidth=lw, label=label, zorder=3)

# Deaths (partial — use what we have)
deaths_df = df[df["Suspected Deaths (Cumulative)"].notna()].copy()
if len(deaths_df) >= 2:
    ax.plot(deaths_df["Date"], deaths_df["Suspected Deaths (Cumulative)"],
            color="#8B0000", linestyle=":", linewidth=1.8,
            label="Suspected deaths", zorder=3)

ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=35, ha="right", fontsize=9)
ax.set_xlim(df["Date"].min() - pd.Timedelta(days=1), df["Date"].max() + pd.Timedelta(days=1))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_xlabel("Date (2026)", fontsize=11)
ax.set_ylabel("Cumulative Count", fontsize=11)
ax.set_title("Figure 2. Cumulative Measles Case Trajectory, Bangladesh 2026\n"
             "(Suspected, Confirmed, Hospitalized, Recovered; 2 April – 2 June 2026)",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=9, loc="upper left", framealpha=0.9)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/fig2_cumulative_trajectory.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/fig2_cumulative_trajectory.png")
plt.close()

# ── Table 1: Summary Statistics ──────────────────────────────────────────────
last = df.iloc[-1]
first_date = df["Date"].min().strftime("%d %b %Y")
last_date  = df["Date"].max().strftime("%d %b %Y")
n_days     = len(df)

total_susp  = int(last["Suspected Cases (Cumulative)"])
total_conf  = int(last["Confirmed Cases (Cumulative)"])
total_hosp  = int(last["Hospitalized (Cumulative)"])
total_rec   = int(last["Recovered (Cumulative)"])
susp_deaths = 504   # from June 2 PDF (most reliable)
conf_deaths = 90

confirm_rate = round(total_conf / total_susp * 100, 1)
hosp_rate    = round(total_hosp / total_susp * 100, 1)
cfr_susp     = round(susp_deaths / total_susp * 100, 2)
cfr_conf     = round(conf_deaths / total_conf * 100, 2)
recovery_rate = round(total_rec / total_hosp * 100, 1)

peak_susp_24h = int(df["Suspected Cases (24h)"].max())
peak_date_susp = df.loc[df["Suspected Cases (24h)"].idxmax(), "Date"].strftime("%d %b %Y")
mean_daily    = round(df["Suspected Cases (24h)"].mean(), 0)

rows = [
    ("Reporting period", f"{first_date} to {last_date} ({n_days} days)"),
    ("Total suspected cases", f"{total_susp:,}"),
    ("Total confirmed cases", f"{total_conf:,}"),
    ("Confirmation rate", f"{confirm_rate}%"),
    ("Total hospitalized (cumulative)", f"{total_hosp:,}"),
    ("Hospitalization rate (of suspected)", f"{hosp_rate}%"),
    ("Total recovered (cumulative)", f"{total_rec:,}"),
    ("Recovery rate (of hospitalized)", f"{recovery_rate}%"),
    ("Total suspected deaths", f"{susp_deaths:,}"),
    ("Total confirmed deaths", f"{conf_deaths:,}"),
    ("Case fatality rate — suspected", f"{cfr_susp}%"),
    ("Case fatality rate — confirmed", f"{cfr_conf}%"),
    ("Peak daily suspected cases", f"{peak_susp_24h:,} ({peak_date_susp})"),
    ("Mean daily suspected cases", f"{int(mean_daily):,}"),
]

t1 = pd.DataFrame(rows, columns=["Indicator", "Value"])
t1.to_csv(f"{DATA}/analysis/table1_summary_stats.csv", index=False)
print(f"\nTable 1 saved: {DATA}/analysis/table1_summary_stats.csv")
print(t1.to_string(index=False))
