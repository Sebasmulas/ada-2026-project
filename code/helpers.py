"""Shared paths, ticker list and loaders used by every notebook."""

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- paths
# Everything is relative to the repository root, so the code runs on any machine.
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
PRICES_DIR = DATA_RAW / "prices"
DATA_PROC = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"

for _d in (PRICES_DIR, DATA_PROC, FIGURES):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- sample
START = "2005-01-01"        # download start (leaves room for the 22-day warm-up before 2007)
END = "2026-11-01"          # fixed end date, so a re-download gives the same sample
SAMPLE_START = "2007-01-01" # first day of the analysis sample
TRAIN_END = "2019-12-31"    # training: 2007-2019, test: 2020 onwards

# ---------------------------------------------------------------- design, fixed before any forecast (see README)
HORIZON = 5                 # forecast target: mean daily variance over t+1 ... t+5
ROLL_WINDOW = 1000          # rolling estimation window, in trading days
WICK_MAX = 0.25             # a bar is unusable if High/Low is more than 25% beyond both Open and Close (bad ticks)

# ---------------------------------------------------------------- tickers
# Yahoo Finance ticker -> (short name used in files, label for figures, group)
TICKERS = {
    "RHM.DE":    ("rheinmetall", "Rheinmetall",       "defence"),
    "LDO.MI":    ("leonardo",    "Leonardo",          "defence"),
    "BA.L":      ("bae",         "BAE Systems",       "defence"),
    "HO.PA":     ("thales",      "Thales",            "defence"),
    "SAAB-B.ST": ("saab",        "Saab",              "defence"),
    "AM.PA":     ("dassault",    "Dassault Aviation", "defence"),
    "^STOXX50E": ("stoxx50",     "EURO STOXX 50",     "market"),
}

# Implied volatility of the EURO STOXX 50 (VSTOXX): a control variable, not a forecast target.
# Yahoo has listed it under different symbols, so notebook 01 tries each and keeps the longest series.
VSTOXX_CANDIDATES = ["^V2TX", "V2TX.DE"]
VSTOXX_CSV = DATA_RAW / "vstoxx.csv"

GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
GPR_XLS = DATA_RAW / "data_gpr_daily_recent.xls"
GPR_CSV = DATA_RAW / "gpr_daily.csv"


def price_path(ticker: str) -> Path:
    """data/raw/prices/<short name>.csv"""
    return PRICES_DIR / f"{TICKERS[ticker][0]}.csv"


# ---------------------------------------------------------------- loaders
def load_prices(ticker: str) -> pd.DataFrame:
    """Read one price file saved by 01_get_data (columns Open, High, Low, Close, Volume)."""
    df = pd.read_csv(price_path(ticker), index_col="Date", parse_dates=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]].apply(pd.to_numeric, errors="coerce")
    return df.sort_index()


def load_gpr() -> pd.DataFrame:
    """Daily GPR on a calendar-day index: columns gpr, acts, threats."""
    g = pd.read_csv(GPR_CSV, parse_dates=["date"]).set_index("date").sort_index()
    return g[["gpr", "acts", "threats"]]


def load_vstoxx() -> pd.Series:
    """Daily VSTOXX close (annualised implied volatility, in %)."""
    v = pd.read_csv(VSTOXX_CSV, index_col="Date", parse_dates=True)["Close"]
    v = pd.to_numeric(v, errors="coerce").dropna().sort_index()
    return v[v > 0]


# ---------------------------------------------------------------- volatility
def daily_variance(p: pd.DataFrame) -> pd.Series:
    """Range-based daily variance in %^2: overnight gap + Parkinson (1980) intraday range.

    var_t = ln(Open_t / Close_{t-1})^2  +  ln(High_t / Low_t)^2 / (4 ln 2)

    The overnight term is needed because the range only covers trading hours, while a
    close-to-close return also contains the gap from yesterday's close to today's open.
    """
    overnight = np.log(p["Open"] / p["Close"].shift(1)) ** 2
    parkinson = np.log(p["High"] / p["Low"]) ** 2 / (4 * np.log(2))
    return (1e4 * (overnight + parkinson)).dropna()


def har_components(v: pd.Series) -> pd.DataFrame:
    """HAR inputs from a daily variance series v (in %^2), all on the same scale.

    The series can be a range-based estimator (daily_variance) or squared returns r^2.

    rv_d   : v_t                            (today)
    rv_w   : mean of v over t-4 ... t       (past week)
    rv_m   : mean of v over t-21 ... t      (past month)
    rv_fwd : mean of v over t+1 ... t+5     (next week = the forecast target)
    """
    out = pd.DataFrame(index=v.index)
    out["rv_d"] = v
    out["rv_w"] = v.rolling(5).mean()
    out["rv_m"] = v.rolling(22).mean()
    # shift(-HORIZON) moves the mean of t+1..t+HORIZON back to row t
    out["rv_fwd"] = v.rolling(HORIZON).mean().shift(-HORIZON)
    return out
