# Portfolio Risk CLI

Command-line tool that reads daily prices for one asset from a CSV file and prints basic risk and return metrics. Built as an AI-assisted coding exercise: spec first, AI-generated code, then review, correction and tests. See [`AUDIT.md`](AUDIT.md) for what the AI generated and what was changed.

## Usage

```bash
python3 risk.py sample_prices.csv
python3 risk.py sample_prices.csv --rf 0.02   # annual risk-free rate as a fraction
```

Example output for `sample_prices.csv`:

```
observations: 5
total return: 3.00%
annualized volatility: 65.08%
max drawdown: 2.94%
sharpe ratio: 3.11
```

The sample is five days of made-up prices, so its volatility and Sharpe ratio are not realistic.

## Input format

CSV with the header `date,price`. Dates are `YYYY-MM-DD`, strictly increasing with no duplicates. Prices are positive numbers. At least 3 rows are required. Blank lines at the end of the file are ignored.

## Metrics

| Metric | Definition |
|---|---|
| Total return | last price / first price - 1 |
| Annualized volatility | sample standard deviation of daily returns x sqrt(252) |
| Max drawdown | largest fall from a running peak, as a fraction of that peak |
| Sharpe ratio | (mean daily return - rf/252) / daily standard deviation x sqrt(252); `n/a` if returns do not vary |

Daily return = price today / price yesterday - 1.

## Error handling

Invalid input (missing file, bad header, bad or duplicate or out-of-order dates, non-numeric or non-positive prices, too few rows, invalid `--rf`, absurdly large price jumps) prints one `error:` line to stderr and exits with code 1. No stack traces for expected errors.

## Tests

```bash
pip install pytest
pytest -v
```

21 tests cover the maths (expected values computed independently of the program), CSV validation, and command-line behaviour.

## Files

| File | Purpose |
|---|---|
| `SPEC.md` | Specification written before any code |
| `risk.py` | The tool |
| `test_risk.py` | Test suite |
| `AUDIT.md` | Review notes: AI output, fixes and verification |
| `risk_ai_original.py` | Untouched AI-generated first version, kept for the audit |
| `sample_prices.csv` | Example input |

## Limitations

One asset only, daily data assumed (252 trading days per year, no check for gaps between dates), no data download, no charts.