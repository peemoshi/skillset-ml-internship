# Portfolio Risk CLI - Specification

## Purpose
Command-line tool that reads daily prices for ONE asset from a CSV file
and prints basic risk and return metrics.

## Usage
python risk.py prices.csv [--rf 0.02]
(--rf = annual risk-free rate as a fraction, default 0.0)

## Input
- CSV with header: date,price
- date in YYYY-MM-DD, strictly increasing, no duplicates
- price: positive number
- at least 3 rows

## Output (printed)
- observations (row count)
- total return
- annualized volatility
- max drawdown
- Sharpe ratio

## Definitions
- daily return r_t = p_t / p_(t-1) - 1
- total return = p_last / p_first - 1
- annualized volatility = sample standard deviation of r (n-1) x sqrt(252)
- Sharpe = (mean(r) - rf/252) / stdev(r) x sqrt(252)
  (if stdev(r) = 0, print "n/a")
- max drawdown = largest (running peak - price) / running peak

## Error handling
- Any invalid input prints one clear message and exits with a non-zero code.
- No Python stack trace for expected errors.
- Invalid cases: file not found, wrong or missing header, non-numeric
  or non-positive price, bad or duplicate or out-of-order date,
  blank rows between data rows (blank lines at end of file are ignored),, fewer than 3 rows, negative or non-numeric --rf.

## Out of scope
Multiple assets, downloading data, charts, any API keys.

## Constraints
Python standard library only (csv, argparse, statistics, math).
Tests written with pytest.