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
| `01_get_data.ipynb` | downloads prices and the VSTOXX (Yahoo Finance) and the daily GPR | `data/raw/` |
| `02_clean.ipynb` | cleans prices, builds returns, HAR inputs, lagged GPR variables | `data/processed/panel.csv`, `figures/fig01_data_overview.png` |

`code/helpers.py` holds the paths, the ticker list, the sample dates and the functions shared by the notebooks.

Running time: under a minute per notebook on a laptop.

## Data

| Data | Source | Period |
|---|---|---|
| Daily prices of Rheinmetall, Leonardo, BAE Systems, Thales, Saab, Dassault Aviation, EURO STOXX 50 | Yahoo Finance via `yfinance`, adjusted for splits and dividends | 2005 – Oct 2026 |
| Daily VSTOXX, the implied volatility of the EURO STOXX 50 (control variable) | Yahoo Finance via `yfinance` | as available |
| Daily Geopolitical Risk index: total, Acts, Threats | Caldara, D. and Iacoviello, M. (2022), "Measuring Geopolitical Risk", *American Economic Review* 112(4); data at matteoiacoviello.com/gpr.htm | 1985 – Oct 2026 |

The raw files used for the results are committed in `data/raw/`. Notebook 01 downloads a file only if it is missing, so the results do not change when the sources are updated.

## Design fixed in advance

These choices were written down on 12 November 2026, **before any out-of-sample forecast was computed**, so that they cannot be tuned on the test period. (Revision on 12 November 2026, still before any forecast: the target moved from squared returns to a range-based variance, because r² is a very noisy proxy. The r² version is kept as a robustness check.) Every result listed here is reported in the paper, whatever its sign. Anything added later is labelled as exploratory.

| Choice | Main specification | Robustness |
|---|---|---|
| Target | ln of mean daily variance over the next 5 trading days; daily variance = overnight gap² + Parkinson range (range-based) | same target built from squared returns r² |
| Benchmark | HAR (day, week, month), OLS, inputs on the same range-based variance | HAR + VSTOXX implied variance (only if a source is found) |
| GPR variables | ln(1 + Threats) and ln(1 + Acts), mean of calendar days t−7 … t−1 | value of day t−1; total GPR instead of the two components |
| Estimation | rolling window of 1,000 trading days, re-estimated every day; last training row is t−5 | 2,000 days; expanding window |
| Test period | 1 January 2020 to the end of the sample | 2020–2021 and 2022–2026 separately; excluding February–March 2022 |
| Forecast in levels | exp(forecast) · exp(½ · residual variance of the window) | — |
| Loss functions | QLIKE (main) and MSE | — |
| Tests | Clark-West for models that nest the HAR, Diebold-Mariano otherwise; HAC variance | — |
| High-risk days | GPR above the 90th percentile of the estimation window (no future data) | 95th percentile |
| Defence vs market | same models on the EURO STOXX 50 | — |
| Neural network | hyperparameters chosen on 2017–2019 only | — |
