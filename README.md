# Geopolitical risk and the volatility of European defence stocks

Advanced Data Analytics, HEC Lausanne, autumn 2026 · Sebastiano Mulas

**Question.** Does geopolitical risk (threats and acts) help forecast the volatility of European defence stocks beyond past volatility, and more than for the broad market?

The project forecasts next week's realized variance of six European defence stocks and the EURO STOXX 50. It compares a HAR benchmark, which uses only past volatility, with models that add the lagged Geopolitical Risk index of Caldara and Iacoviello, split into threats and acts.

## Install

```
pip install -r requirements.txt
```

## Run, in this order

All notebooks are in `code/`. Run each one top to bottom (Restart Kernel → Run All).

| Notebook | What it does | Output |
|---|---|---|
| `01_get_data.ipynb` | downloads prices (Yahoo Finance) and the daily GPR | `data/raw/` |
| `02_clean.ipynb` | cleans prices, builds returns, HAR inputs, lagged GPR variables | `data/processed/panel.csv`, `figures/fig01_data_overview.png` |

`code/helpers.py` holds the paths, the ticker list, the sample dates and the functions shared by the notebooks.

Running time: under a minute per notebook on a laptop.

## Data

| Data | Source | Period |
|---|---|---|
| Daily prices of Rheinmetall, Leonardo, BAE Systems, Thales, Saab, Dassault Aviation, EURO STOXX 50 | Yahoo Finance via `yfinance`, adjusted for splits and dividends | 2005 – Oct 2026 |
| Daily Geopolitical Risk index: total, Acts, Threats | Caldara, D. and Iacoviello, M. (2022), "Measuring Geopolitical Risk", *American Economic Review* 112(4); data at matteoiacoviello.com/gpr.htm | 1985 – Oct 2026 |

The raw files used for the results are committed in `data/raw/`. Notebook 01 downloads a file only if it is missing, so the results do not change when the sources are updated.
