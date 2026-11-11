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


# ---------------------------------------------------------------- volatility
def har_components(r: pd.Series) -> pd.DataFrame:
    """HAR inputs from daily log returns r (in %), all on the same scale (average daily variance).

    rv_d   : r_t^2                          (today)
    rv_w   : mean of r^2 over t-4 ... t     (past week)
    rv_m   : mean of r^2 over t-21 ... t    (past month)
    rv_fwd : mean of r^2 over t+1 ... t+5   (next week = the forecast target)
    """
    r2 = r**2
    out = pd.DataFrame(index=r.index)
    out["rv_d"] = r2
    out["rv_w"] = r2.rolling(5).mean()
    out["rv_m"] = r2.rolling(22).mean()
    # shift(-5) moves the mean of t+1..t+5 back to row t
    out["rv_fwd"] = r2.rolling(5).mean().shift(-5)
    return out
