"""
Computational Epidemiology - Figure 12: R0 and Rt Estimation
R0: Wallinga-Lipsitch exponential growth method (exponential growth phase, days 1-14)
Rt: Cori et al. (2013) Bayesian sliding-window method (7-day window)
Serial interval: Gamma(mean=12 days, SD=3 days) — standard measles
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import gamma as gamma_dist
import warnings
warnings.filterwarnings("ignore")

DATA = "/Users/khalilur/Documents/AIWORK/measles_national_summary.csv"
OUT  = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"

# ── Load data ──────────────────────────────────────────────────────────────
df = pd.read_csv(DATA, parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)
df["day"]           = (df["Date"] - df["Date"].iloc[0]).dt.days + 1
df["new_suspected"] = df["Suspected Cases (24h)"].fillna(0).clip(lower=0).astype(int)
df["cum_suspected"] = df["Suspected Cases (Cumulative)"].ffill().astype(int)

print(f"Period : {df['Date'].iloc[0].date()} to {df['Date'].iloc[-1].date()} ({len(df)} days)")
print(f"Total  : {df['cum_suspected'].iloc[-1]:,} suspected cumulative")

# ── Serial interval (measles standard) ────────────────────────────────────
SI_MEAN, SI_SD = 12.0, 3.0
SI_SHAPE = (SI_MEAN / SI_SD) ** 2      # 16.0
SI_SCALE = (SI_SD ** 2) / SI_MEAN      # 0.75
si_days  = np.arange(1, 31)
si_pmf   = gamma_dist.pdf(si_days, a=SI_SHAPE, scale=SI_SCALE)
si_pmf  /= si_pmf.sum()

# ── R0 via exponential growth (first 14 days) ─────────────────────────────
phase = df.iloc[:14]
t_g   = phase["day"].values.astype(float)
I_g   = phase["cum_suspected"].values.astype(float)

def exp_model(t, I0, r):
    return I0 * np.exp(r * t)

popt, pcov = curve_fit(exp_model, t_g, I_g, p0=[500, 0.15], maxfev=10000)
I0_fit, r_fit = popt
r_se = np.sqrt(np.diag(pcov))[1]

# R0 formula: Wallinga-Lipsitch (2007) for gamma-distributed SI
# R0 = (1 + r * mu^2 / (mu^2 / sigma^2)) for gamma
# Simplified: R0 = (1 + r * b)^a  where b=scale, a=shape (moment-generating function)
R0      = (1 + r_fit  * SI_SCALE) ** SI_SHAPE
R0_low  = (1 + (r_fit - 1.96*r_se) * SI_SCALE) ** SI_SHAPE
R0_high = (1 + (r_fit + 1.96*r_se) * SI_SCALE) ** SI_SHAPE
DT      = np.log(2) / r_fit

print(f"\nR0 Estimation:")
print(f"  Growth rate r = {r_fit:.4f}/day  (95% CI {r_fit-1.96*r_se:.4f}–{r_fit+1.96*r_se:.4f})")
print(f"  Doubling time = {DT:.1f} days")
print(f"  R0 = {R0:.2f}  (95% CI: {R0_low:.2f}–{R0_high:.2f})")

# ── Rt estimation: Cori Bayesian method ───────────────────────────────────
# Seed with back-projected pre-study cases (March 15 - April 1, 18 days)
# The outbreak started ~March 15; by April 2 there were 3,709 cumulative cases.
# Back-project daily incidence using r_fit to populate the SI window.
SEED_DAYS = 18   # March 15 to April 1 inclusive
seed_incidence = np.array([
    max(0, df["cum_suspected"].iloc[0] / np.expm1(r_fit * SEED_DAYS)
        * np.exp(r_fit * d))
    for d in range(SEED_DAYS)
])
incidence_full = np.concatenate([seed_incidence, df["new_suspected"].values.astype(float)])
incidence      = incidence_full[SEED_DAYS:]   # study-period only, for plotting
n_full = len(incidence_full)
n      = len(df)
TAU    = 7
a0, b0 = 1.0, 5.0

# Infectivity Lambda on full (seeded) series
Lambda_full = np.zeros(n_full)
for t in range(n_full):
    for s, w in enumerate(si_pmf):
        ts = t - (s + 1)
        if ts >= 0:
            Lambda_full[t] += incidence_full[ts] * w

# Compute Rt on the study-period portion only (offset by SEED_DAYS)
Rt_mean = np.full(n, np.nan)
Rt_low  = np.full(n, np.nan)
Rt_high = np.full(n, np.nan)

for t_study in range(TAU, n):
    t = t_study + SEED_DAYS
    wI = incidence_full[t - TAU + 1 : t + 1].sum()
    wL = Lambda_full[t - TAU + 1 : t + 1].sum()
    if wL > 0:
        a_t = a0 + wI
        b_t = 1.0 / (1.0 / b0 + wL)
        Rt_mean[t_study] = a_t * b_t
        Rt_low[t_study]  = gamma_dist.ppf(0.025, a=a_t, scale=b_t)
        Rt_high[t_study] = gamma_dist.ppf(0.975, a=a_t, scale=b_t)

valid_rt = ~np.isnan(Rt_mean)
print(f"\nRt Summary:")
print(f"  Peak Rt = {np.nanmax(Rt_mean):.2f} (Day {np.nanargmax(Rt_mean)+1}, {df['Date'].iloc[np.nanargmax(Rt_mean)].date()})")
print(f"  Final Rt = {Rt_mean[-1]:.2f} (95% CI: {Rt_low[-1]:.2f}–{Rt_high[-1]:.2f})")
print(f"  Days Rt > 1: {(Rt_mean[valid_rt] > 1).sum()} / {valid_rt.sum()}")

# Save Rt table
rt_df = df[["Date","day","new_suspected"]].copy()
rt_df["Rt"]     = Rt_mean
rt_df["Rt_low"] = Rt_low
rt_df["Rt_high"]= Rt_high
rt_df.to_csv(
    "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_rt_estimates.csv",
    index=False,
)

# ── FIGURE 12 ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(21, 7))
dates = df["Date"].values

# Panel A: Epidemic curve + exponential fit
ax = axes[0]
ax.bar(dates, incidence, color="#6baed6", alpha=0.75, width=0.9, zorder=2,
       label="Daily new suspected cases")
t_fine = np.linspace(1, 14, 200)
ax.plot(
    df["Date"].iloc[0] + pd.to_timedelta(t_fine - 1, "D"),
    exp_model(t_fine, I0_fit, r_fit),
    "r-", linewidth=2.5, zorder=5,
    label=f"Exponential fit (days 1-14)\nr = {r_fit:.4f}/day, DT = {DT:.1f} days",
)
ax.axvline(df["Date"].iloc[13], color="red", linestyle="--", alpha=0.6,
           label="End of growth phase")
ax.text(0.97, 0.97,
        f"R0 = {R0:.2f}\n95% CI: {R0_low:.2f}–{R0_high:.2f}\n\n"
        f"Method: Wallinga-Lipsitch\nSI: Gamma(mean=12d, SD=3d)",
        transform=ax.transAxes, ha="right", va="top", fontsize=9,
        bbox=dict(boxstyle="round", fc="#fff7bc", alpha=0.95))
ax.set_title("(a) Epidemic Curve and R0 Estimation\n(Exponential Growth Phase, Days 1-14)",
             fontsize=10, fontweight="bold")
ax.set_xlabel("Date (2026)", fontsize=9)
ax.set_ylabel("Daily New Suspected Cases", fontsize=9)
ax.legend(fontsize=8, loc="upper left")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.tick_params(axis="x", rotation=30)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.2)

# Panel B: Rt over time
ax = axes[1]
ax.fill_between(dates, Rt_low, Rt_high, alpha=0.22, color="#de2d26",
                label="95% Credible Interval")
ax.plot(dates, Rt_mean, color="#de2d26", linewidth=2.2,
        label=f"Rt (Cori, 7-day window)")
ax.axhline(1.0, color="black", linewidth=1.8, linestyle="--",
           label="Rt = 1.0 (epidemic threshold)")
ax.axvline(pd.Timestamp("2026-04-05"), color="#756bb1", linestyle=":",
           linewidth=1.5, label="Reactive MR campaign (5 Apr)")

# Shade below threshold
ax.fill_between(dates,
                np.where(Rt_mean < 1, Rt_mean, 1),
                1, alpha=0.15, color="green", label="Rt < 1 zone")
ax.fill_between(dates,
                np.where(Rt_mean > 1, Rt_mean, 1),
                1, alpha=0.10, color="red", label="Rt > 1 zone")

peak_day = np.nanargmax(Rt_mean)
ax.annotate(f"Peak Rt = {np.nanmax(Rt_mean):.2f}\n({df['Date'].iloc[peak_day].date()})",
            xy=(dates[peak_day], np.nanmax(Rt_mean)),
            xytext=(30, -30), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
            fontsize=8.5, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#de2d26", alpha=0.9))
ax.text(0.97, 0.03,
        f"Final Rt = {Rt_mean[-1]:.2f}\n(95% CI: {Rt_low[-1]:.2f}–{Rt_high[-1]:.2f})",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
        bbox=dict(boxstyle="round", fc="#fff7bc", alpha=0.95))
ax.set_title("(b) Time-Varying Effective Reproduction Number (Rt)\n"
             "Cori et al. (2013) Bayesian Method, 7-Day Sliding Window",
             fontsize=10, fontweight="bold")
ax.set_xlabel("Date (2026)", fontsize=9)
ax.set_ylabel("Effective Reproduction Number (Rt)", fontsize=9)
ax.legend(fontsize=7.5, loc="upper right", ncol=2)
ax.set_ylim(0, np.nanmax(Rt_mean) + 0.4)
ax.tick_params(axis="x", rotation=30)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.2)

# Panel C: R0 comparison + serial interval
ax  = axes[2]
ax2 = ax.twinx()

# Serial interval density
si_x = np.linspace(0, 30, 300)
si_y = gamma_dist.pdf(si_x, a=SI_SHAPE, scale=SI_SCALE)
ax2.fill_between(si_x, si_y, alpha=0.30, color="#74c476")
ax2.plot(si_x, si_y, color="#238b45", linewidth=1.8,
         label=f"SI distribution\nGamma(mean=12d, SD=3d)")
ax2.axvline(SI_MEAN, color="#238b45", linestyle="--", linewidth=1.2)
ax2.set_ylabel("Serial Interval Probability Density", fontsize=8, color="#238b45")
ax2.tick_params(axis="y", colors="#238b45")
ax2.set_ylim(0, si_y.max() * 4.5)
ax2.set_xlim(0, 30)

# R0 bar comparison
diseases = ["Influenza\n(seasonal)", "COVID-19\n(Delta)", "Ebola\n(2014)", "2026 BD\nMeasles", "Measles\n(endemic)"]
r0_comp  = [1.3, 5.1, 1.8, round(R0, 2), 15.0]
clrs     = ["#9ecae1","#9ecae1","#9ecae1","#de2d26","#fcbba1"]
bars2 = ax.bar(diseases, r0_comp, color=clrs, edgecolor="white", linewidth=0.5,
               alpha=0.85, zorder=3)
ax.axhline(1.0, color="black", linewidth=1.0, linestyle="--", alpha=0.5)
for bar, val in zip(bars2, r0_comp):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
            f"{val:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_ylabel("Basic Reproduction Number (R0)", fontsize=9)
ax.set_ylim(0, 18)
ax.set_title(f"(c) R0 in Disease Context\n+ Measles Serial Interval Distribution",
             fontsize=10, fontweight="bold")
ax.spines[["top"]].set_visible(False)
ax.grid(axis="y", alpha=0.2)
h1, l1 = ax2.get_legend_handles_labels()
ax2.legend(h1, l1, fontsize=8, loc="upper right")

fig.suptitle(
    "Figure 12. Transmission Dynamics of the 2026 Bangladesh Measles Outbreak\n"
    "R0 Estimated by Exponential Growth (Days 1-14); Rt by Cori et al. (2013) Bayesian Method",
    fontsize=12, fontweight="bold", y=1.02,
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig12_r0_rt.png", dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT}/fig12_r0_rt.png")

# Print final results for manuscript
print(f"\n=== FOR MANUSCRIPT ===")
print(f"R0 = {R0:.2f} (95% CI: {R0_low:.2f}–{R0_high:.2f})")
print(f"Doubling time = {DT:.1f} days")
print(f"Growth rate r = {r_fit:.4f}/day")
print(f"Peak Rt = {np.nanmax(Rt_mean):.2f} on Day {np.nanargmax(Rt_mean)+1} ({df['Date'].iloc[np.nanargmax(Rt_mean)].date()})")
print(f"Final Rt (Jun 2) = {Rt_mean[-1]:.2f} (95% CI: {Rt_low[-1]:.2f}–{Rt_high[-1]:.2f})")
plt.close()
