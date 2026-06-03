"""
Figure 1: Epidemic curve — daily new suspected and confirmed measles cases
with 7-day rolling average overlay.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import numpy as np

DATA = "/Users/khalilur/Documents/AIWORK"
OUT  = "/Users/khalilur/Documents/AIWORK/analysis/figures"

df = pd.read_csv(f"{DATA}/measles_national_summary.csv", parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

suspected  = df["Suspected Cases (24h)"]
confirmed  = df["Confirmed Cases (24h)"]
dates      = df["Date"]

roll7_susp = suspected.rolling(7, center=True).mean()
roll7_conf = confirmed.rolling(7, center=True).mean()

fig, ax = plt.subplots(figsize=(13, 5.5))

# Bars
bar_width = 0.7
ax.bar(dates, suspected, width=bar_width, color="#E07B54", alpha=0.85, label="Suspected cases (24 h)", zorder=2)
ax.bar(dates, confirmed, width=bar_width, color="#3A6EA5", alpha=0.9,  label="Confirmed cases (24 h)", zorder=3)

# Rolling averages
ax.plot(dates, roll7_susp, color="#A0522D", linewidth=2.2, linestyle="-",
        label="7-day rolling avg (suspected)", zorder=4)
ax.plot(dates, roll7_conf, color="#1A3A6A", linewidth=2.2, linestyle="--",
        label="7-day rolling avg (confirmed)", zorder=4)

# Peak annotation
peak_idx = suspected.idxmax()
peak_date = dates[peak_idx]
peak_val  = suspected[peak_idx]
ax.annotate(f"Peak: {int(peak_val):,}\n({peak_date.strftime('%d %b')})",
            xy=(peak_date, peak_val),
            xytext=(peak_date + pd.Timedelta(days=3), peak_val - 80),
            fontsize=9, color="#A0522D",
            arrowprops=dict(arrowstyle="->", color="#A0522D", lw=1.2))

# Axis formatting
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=35, ha="right", fontsize=9)
ax.set_xlim(dates.min() - pd.Timedelta(days=1), dates.max() + pd.Timedelta(days=1))
ax.set_ylim(0, suspected.max() * 1.18)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

ax.set_xlabel("Date (2026)", fontsize=11)
ax.set_ylabel("Number of Cases", fontsize=11)
ax.set_title("Figure 1. Epidemic Curve of the 2026 Measles Outbreak in Bangladesh\n"
             "(Daily Suspected and Confirmed Cases, 2 April – 2 June 2026)", fontsize=12, fontweight="bold")

ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=1)
ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
fig.savefig(f"{OUT}/fig1_epidemic_curve.png", dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}/fig1_epidemic_curve.png")
plt.close()
