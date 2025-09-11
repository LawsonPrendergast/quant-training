
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.optimize import newton
import matplotlib.pyplot as plt
import seaborn as sns
from QuantLib import Date, Actual365Fixed

# --- Parameters ---
TICKER = "AAPL"
r = 0.01  # flat risk-free rate
day_count = Actual365Fixed()

# --- Black–Scholes call price ---
def bs_call_price(S, K, r, T, sigma):
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return np.nan
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

# --- Fetch market data ---
ticker = yf.Ticker(TICKER)
S0 = float(ticker.history(period="1d")["Close"].iloc[-1])

imp_vol_rows = []

# --- Build implied vol table across expiries & strikes ---
for expiry_str in ticker.options:
    # Parse expiry into QuantLib Date and compute year fraction T
    year, month, day = map(int, expiry_str.split("-"))
    expiry_date = Date(day, month, year)
    T = day_count.yearFraction(Date().todaysDate(), expiry_date)
    if T <= 0:
        continue

    # Pull option chain (calls only for this demo) and mid prices
    calls = ticker.option_chain(expiry_str).calls
    if calls.empty:
        continue
    calls = calls.copy()
    calls["mid"] = (calls["bid"].fillna(0) + calls["ask"].fillna(0)) / 2

    # Row-wise implied vol solver
    def _imp_vol_call(row):
        K = float(row["strike"])  # ensure float
        market_price = float(row["mid"]) if pd.notna(row["mid"]) else np.nan
        if not np.isfinite(market_price) or market_price <= 0:
            return np.nan
        try:
            return newton(lambda vol: bs_call_price(S0, K, r, T, vol) - market_price, 0.2, maxiter=50)
        except Exception:
            return np.nan

    calls["imp_vol"] = calls.apply(_imp_vol_call, axis=1)
    valid = calls.loc[calls["imp_vol"].astype(float) > 0, ["strike", "imp_vol"]]
    for _, rr in valid.iterrows():
        imp_vol_rows.append({
            "expiry": expiry_str,
            "strike": float(rr["strike"]),
            "imp_vol": float(rr["imp_vol"]),
        })

# --- Assemble DataFrame, tidy, and save ---
df_iv = pd.DataFrame(imp_vol_rows)
if not df_iv.empty:
    df_iv = df_iv.sort_values(["expiry", "strike"]).reset_index(drop=True)
    df_iv.to_csv("implied_vol_points.csv", index=False)
    print(f"Saved implied_vol_points.csv with {len(df_iv)} rows across {df_iv['expiry'].nunique()} expiries.")

    # Pivot to surface for plotting
    surface = df_iv.pivot(index="expiry", columns="strike", values="imp_vol")
    surface = surface.sort_index()
    surface = surface.reindex(sorted(surface.columns), axis=1)

    # Plot heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(surface, cmap="viridis", cbar_kws={"label": "Implied Vol"})
    plt.title(f"Implied Volatility Surface – {TICKER}")
    plt.ylabel("Expiry Date")
    plt.xlabel("Strike")
    plt.tight_layout()
    plt.show()
else:
    print("No implied vols could be solved (empty surface). Try again later or check data connectivity.")
