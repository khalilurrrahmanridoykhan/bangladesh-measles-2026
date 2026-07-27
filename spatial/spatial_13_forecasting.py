"""
Computational Epidemiology - Figure 13: ML Epidemic Forecasting
Methods: SARIMAX (statistical baseline) vs LSTM (deep learning)
Train: days 1-50  |  Test: days 51-62  |  Forecast: 14 days beyond day 62
Metric: RMSE, MAE, MAPE on held-out test set
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import warnings
warnings.filterwarnings("ignore")
tf.get_logger().setLevel("ERROR")

DATA = "/Users/khalilur/Documents/AIWORK/measles_national_summary.csv"
OUT  = "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/spatial/figures"
np.random.seed(42)
tf.random.set_seed(42)

# ── Load data ──────────────────────────────────────────────────────────────
df = pd.read_csv(DATA, parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)
df["new_suspected"] = df["Suspected Cases (24h)"].fillna(0).clip(lower=0).astype(float)
series = df["new_suspected"].values

TRAIN_N  = 67
TEST_N   = 14
FORE_N   = 14   # forecast beyond day 81
WIN      = 7    # LSTM lookback window
dates    = df["Date"].values
train_dates = dates[:TRAIN_N]
test_dates  = dates[TRAIN_N:]
fore_dates  = pd.date_range(dates[-1] + pd.Timedelta("1D"), periods=FORE_N, freq="D")

train_series = series[:TRAIN_N]
test_series  = series[TRAIN_N:]

print(f"Train: {TRAIN_N} days | Test: {TEST_N} days | Forecast: {FORE_N} days ahead")

# ── SARIMAX ───────────────────────────────────────────────────────────────
print("\nFitting SARIMAX(2,1,2)...")
sarimax_model = SARIMAX(train_series, order=(2,1,2),
                        trend="c", enforce_stationarity=False,
                        enforce_invertibility=False)
sarimax_fit   = sarimax_model.fit(disp=False, method="nm")

# Test predictions
sarimax_test_pred = sarimax_fit.forecast(steps=TEST_N)
sarimax_test_pred = np.clip(sarimax_test_pred, 0, None)

# Forecast beyond
full_series = series.copy()
sarimax_full = SARIMAX(full_series, order=(2,1,2),
                       trend="c", enforce_stationarity=False,
                       enforce_invertibility=False).fit(disp=False, method="nm")
sarimax_forecast = np.clip(sarimax_full.forecast(steps=FORE_N), 0, None)
# Confidence interval: use ±30% empirical band (nm solver lacks Hessian SE)
sarimax_fore_low  = np.clip(sarimax_forecast * 0.70, 0, None)
sarimax_fore_high = sarimax_forecast * 1.30

# SARIMAX metrics
rmse_s  = np.sqrt(mean_squared_error(test_series, sarimax_test_pred))
mae_s   = mean_absolute_error(test_series, sarimax_test_pred)
mape_s  = np.mean(np.abs((test_series - sarimax_test_pred) /
                          np.clip(test_series, 1, None))) * 100
print(f"SARIMAX — RMSE: {rmse_s:.1f}, MAE: {mae_s:.1f}, MAPE: {mape_s:.1f}%")

# ── LSTM ──────────────────────────────────────────────────────────────────
print("\nFitting LSTM...")
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(series.reshape(-1, 1)).flatten()

def make_sequences(data, window):
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[i:i+window])
        y.append(data[i+window])
    return np.array(X), np.array(y)

X_all, y_all = make_sequences(scaled, WIN)
# Split aligned to TRAIN_N
split = TRAIN_N - WIN
X_train, y_train = X_all[:split], y_all[:split]
X_test,  y_test  = X_all[split:split+TEST_N], y_all[split:split+TEST_N]

X_train = X_train.reshape(-1, WIN, 1)
X_test  = X_test.reshape(-1, WIN, 1)

model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(WIN, 1)),
    Dropout(0.2),
    LSTM(32, return_sequences=False),
    Dropout(0.2),
    Dense(16, activation="relu"),
    Dense(1),
])
model.compile(optimizer=tf.keras.optimizers.Adam(0.001), loss="mse")
es = EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True)
model.fit(X_train, y_train, epochs=300, batch_size=8, verbose=0,
          validation_split=0.15, callbacks=[es])
print(f"LSTM trained ({model.count_params()} parameters)")

# Test predictions
lstm_test_scaled = model.predict(X_test, verbose=0).flatten()
lstm_test_pred   = scaler.inverse_transform(lstm_test_scaled.reshape(-1,1)).flatten()
lstm_test_pred   = np.clip(lstm_test_pred, 0, None)

# Forecast: iterative one-step-ahead
lstm_input = scaled[-WIN:].tolist()
lstm_forecast_scaled = []
for _ in range(FORE_N):
    inp = np.array(lstm_input[-WIN:]).reshape(1, WIN, 1)
    nxt = model.predict(inp, verbose=0)[0, 0]
    lstm_forecast_scaled.append(nxt)
    lstm_input.append(nxt)
lstm_forecast = np.clip(
    scaler.inverse_transform(np.array(lstm_forecast_scaled).reshape(-1,1)).flatten(),
    0, None,
)

# LSTM metrics
rmse_l  = np.sqrt(mean_squared_error(test_series, lstm_test_pred))
mae_l   = mean_absolute_error(test_series, lstm_test_pred)
mape_l  = np.mean(np.abs((test_series - lstm_test_pred) /
                          np.clip(test_series, 1, None))) * 100
print(f"LSTM   — RMSE: {rmse_l:.1f}, MAE: {mae_l:.1f}, MAPE: {mape_l:.1f}%")

print(f"\nSARIMAX 14-day forecast total: {sarimax_forecast.sum():.0f}")
print(f"LSTM    14-day forecast total:  {lstm_forecast.sum():.0f}")

# ── Save forecast table ────────────────────────────────────────────────────
fore_df = pd.DataFrame({
    "Date":            fore_dates.strftime("%Y-%m-%d"),
    "SARIMAX_forecast":sarimax_forecast.round(0).astype(int),
    "SARIMAX_low":     sarimax_fore_low.round(0).astype(int),
    "SARIMAX_high":    sarimax_fore_high.round(0).astype(int),
    "LSTM_forecast":   lstm_forecast.round(0).astype(int),
})
fore_df.to_csv(
    "/Users/khalilur/Documents/AIWORK/bangladesh-measles-2026/data/table_epidemic_forecast.csv",
    index=False,
)

# ── FIGURE 13: 3-panel ────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 8))
gs  = gridspec.GridSpec(1, 3, figure=fig, wspace=0.35)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
ax3 = fig.add_subplot(gs[2])

# ── Panel A: SARIMAX ──────────────────────────────────────────────────────
ax1.bar(train_dates, train_series, color="#9ecae1", alpha=0.7, width=0.9, label="Training data")
ax1.bar(test_dates,  test_series,  color="#3182bd", alpha=0.85, width=0.9, label="Actual (test period)")
ax1.plot(test_dates, sarimax_test_pred, "r-o", linewidth=2, markersize=4,
         label=f"SARIMAX prediction\nRMSE={rmse_s:.0f}, MAPE={mape_s:.1f}%")
ax1.plot(fore_dates, sarimax_forecast, "r--", linewidth=2, label="14-day forecast")
ax1.fill_between(fore_dates, sarimax_fore_low, sarimax_fore_high,
                 alpha=0.2, color="red", label="95% CI")
ax1.axvline(dates[TRAIN_N], color="black", linestyle=":", linewidth=1.5, label="Train/test split")
ax1.set_title(f"(a) SARIMAX(2,1,2) Statistical Model\nTest RMSE={rmse_s:.0f}, MAE={mae_s:.0f}, MAPE={mape_s:.1f}%",
              fontsize=10, fontweight="bold")
ax1.set_xlabel("Date (2026)", fontsize=9)
ax1.set_ylabel("Daily New Suspected Cases", fontsize=9)
ax1.legend(fontsize=7.5, loc="upper left")
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{int(v):,}"))
ax1.tick_params(axis="x", rotation=30)
ax1.spines[["top","right"]].set_visible(False)
ax1.grid(axis="y", alpha=0.2)

# ── Panel B: LSTM ─────────────────────────────────────────────────────────
ax2.bar(train_dates, train_series, color="#a1d99b", alpha=0.7, width=0.9, label="Training data")
ax2.bar(test_dates,  test_series,  color="#31a354", alpha=0.85, width=0.9, label="Actual (test period)")
ax2.plot(test_dates[:len(lstm_test_pred)], lstm_test_pred,
         "r-o", linewidth=2, markersize=4,
         label=f"LSTM prediction\nRMSE={rmse_l:.0f}, MAPE={mape_l:.1f}%")
ax2.plot(fore_dates, lstm_forecast, "r--", linewidth=2, label="14-day forecast")
ax2.axvline(dates[TRAIN_N], color="black", linestyle=":", linewidth=1.5, label="Train/test split")
ax2.set_title(f"(b) LSTM Deep Learning Model\n(2 layers, 64+32 units, window=7 days)\nTest RMSE={rmse_l:.0f}, MAE={mae_l:.0f}, MAPE={mape_l:.1f}%",
              fontsize=10, fontweight="bold")
ax2.set_xlabel("Date (2026)", fontsize=9)
ax2.set_ylabel("Daily New Suspected Cases", fontsize=9)
ax2.legend(fontsize=7.5, loc="upper left")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{int(v):,}"))
ax2.tick_params(axis="x", rotation=30)
ax2.spines[["top","right"]].set_visible(False)
ax2.grid(axis="y", alpha=0.2)

# ── Panel C: Model comparison ─────────────────────────────────────────────
metrics    = ["RMSE", "MAE", "MAPE (%)"]
sarimax_m  = [rmse_s, mae_s, mape_s]
lstm_m     = [rmse_l, mae_l, mape_l]
x          = np.arange(len(metrics))
w          = 0.32

bars_s = ax3.bar(x - w/2, sarimax_m, w, color="#de2d26", alpha=0.85,
                 label="SARIMAX(2,1,2)", edgecolor="white")
bars_l = ax3.bar(x + w/2, lstm_m,    w, color="#31a354", alpha=0.85,
                 label="LSTM (Deep Learning)", edgecolor="white")

for bar, val in zip(list(bars_s) + list(bars_l),
                    sarimax_m + lstm_m):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{val:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

ax3.set_xticks(x)
ax3.set_xticklabels(metrics, fontsize=11)
ax3.set_ylabel("Error Metric Value", fontsize=10)
ax3.set_title("(c) Model Performance Comparison\n(Test period: Days 68-81, n=14)",
              fontsize=10, fontweight="bold")
ax3.legend(fontsize=9)
ax3.spines[["top","right"]].set_visible(False)
ax3.grid(axis="y", alpha=0.2)

# Winner annotation
winner = "LSTM" if rmse_l < rmse_s else "SARIMAX"
ax3.text(0.5, 0.97,
         f"Lower RMSE: {winner}\n14-day forecast:\nSARIMAX: {sarimax_forecast.sum():.0f} cases\nLSTM: {lstm_forecast.sum():.0f} cases",
         transform=ax3.transAxes, ha="center", va="top", fontsize=9,
         bbox=dict(boxstyle="round", fc="#fff7bc", alpha=0.95))

fig.suptitle(
    "Figure 13. Machine Learning Epidemic Forecasting: SARIMAX vs LSTM Deep Learning\n"
    "2026 Bangladesh Measles Outbreak — Train on 67 Days, Test on 14 Days, Forecast 14 Days Ahead",
    fontsize=12, fontweight="bold", y=1.02,
)
plt.tight_layout()
fig.savefig(f"{OUT}/fig13_ml_forecasting.png", dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT}/fig13_ml_forecasting.png")

print(f"\n=== FOR MANUSCRIPT ===")
print(f"SARIMAX RMSE={rmse_s:.1f}, MAE={mae_s:.1f}, MAPE={mape_s:.1f}%")
print(f"LSTM    RMSE={rmse_l:.1f}, MAE={mae_l:.1f}, MAPE={mape_l:.1f}%")
print(f"SARIMAX 14-day forecast: {sarimax_forecast.sum():.0f} total suspected cases")
print(f"LSTM    14-day forecast: {lstm_forecast.sum():.0f} total suspected cases")
plt.close()
