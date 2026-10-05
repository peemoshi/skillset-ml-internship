#!/usr/bin/env python3
"""Print basic risk and return metrics for one asset from a CSV of daily prices."""

import argparse
import csv
import datetime
import math
import statistics
import sys

TRADING_DAYS = 252
ZERO_VOLATILITY_TOLERANCE = 1e-12  # Avoid treating floating-point noise as meaningful volatility.
MIN_ROWS = 3
EXPECTED_HEADER = ["date", "price"]


class InputError(Exception):
    """Raised for any expected problem with the user's input."""


def parse_rf(text):
    """Validate the --rf argument: a non-negative, finite number."""
    try:
        rf = float(text)
    except ValueError:
        raise InputError(f"--rf must be a number, got {text!r}")
    if not math.isfinite(rf) or rf < 0:
        raise InputError(f"--rf must be a non-negative number, got {text!r}")
    return rf


def parse_date(text, line_no):
    if len(text) != 10:
        raise InputError(f"line {line_no}: bad date {text!r}, expected YYYY-MM-DD")
    try:
        return datetime.datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise InputError(f"line {line_no}: bad date {text!r}, expected YYYY-MM-DD")


def parse_price(text, line_no):
    try:
        price = float(text)
    except ValueError:
        raise InputError(f"line {line_no}: price {text!r} is not a number")
    if not math.isfinite(price) or price <= 0:
        raise InputError(f"line {line_no}: price {text!r} must be a positive number")
    return price


def load_prices(path):
    """Read and validate the CSV; return the list of prices in date order."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
    except FileNotFoundError:
        raise InputError(f"file not found: {path}")
    except UnicodeDecodeError:
        raise InputError(f"{path} is not valid UTF-8 text")
    except OSError as e:
        raise InputError(f"cannot read {path}: {e.strerror or e}")
    except csv.Error as e:
        raise InputError(f"cannot parse {path} as CSV: {e}")

    if not rows or rows[0] != EXPECTED_HEADER:
        raise InputError("header must be exactly: date,price")

    while len(rows) > 1 and (not rows[-1] or all(cell.strip() == "" for cell in rows[-1])):
        rows.pop()

    prices = []
    previous_date = None
    for line_no, row in enumerate(rows[1:], start=2):
        if not row or all(cell.strip() == "" for cell in row):
            raise InputError(f"line {line_no}: blank row")
        if len(row) != 2:
            raise InputError(f"line {line_no}: expected 2 columns, got {len(row)}")
        date = parse_date(row[0], line_no)
        price = parse_price(row[1], line_no)
        if previous_date is not None:
            if date == previous_date:
                raise InputError(f"line {line_no}: duplicate date {row[0]}")
            if date < previous_date:
                raise InputError(f"line {line_no}: date {row[0]} is out of order")
        previous_date = date
        prices.append(price)

    if len(prices) < MIN_ROWS:
        raise InputError(f"need at least {MIN_ROWS} rows of data, got {len(prices)}")
    return prices


def daily_returns(prices):
    return [curr / prev - 1 for prev, curr in zip(prices, prices[1:])]


def total_return(prices):
    return prices[-1] / prices[0] - 1


def annualized_volatility(returns):
    return statistics.stdev(returns) * math.sqrt(TRADING_DAYS)


def max_drawdown(prices):
    peak = prices[0]
    worst = 0.0
    for price in prices:
        peak = max(peak, price)
        worst = max(worst, (peak - price) / peak)
    return worst


def sharpe_ratio(returns, rf):
    """Annualized Sharpe ratio, or None if the returns have zero volatility."""
    stdev = statistics.stdev(returns)
    if stdev < ZERO_VOLATILITY_TOLERANCE:
        return None
    excess = statistics.mean(returns) - rf / TRADING_DAYS
    return excess / stdev * math.sqrt(TRADING_DAYS)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Print risk and return metrics for one asset from a CSV of daily prices."
    )
    parser.add_argument("csv_path", metavar="prices.csv", help="CSV file with header date,price")
    parser.add_argument(
        "--rf",
        default="0.0",
        help="annual risk-free rate as a fraction (default: 0.0)",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        rf = parse_rf(args.rf)
        prices = load_prices(args.csv_path)
        returns = daily_returns(prices)
        if not all(math.isfinite(value) for value in returns):
            raise InputError("price changes are too extreme to compute metrics")
    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    sharpe = sharpe_ratio(returns, rf)

    print(f"observations: {len(prices)}")
    print(f"total return: {total_return(prices):.2%}")
    print(f"annualized volatility: {annualized_volatility(returns):.2%}")
    print(f"max drawdown: {max_drawdown(prices):.2%}")
    print(f"sharpe ratio: {'n/a' if sharpe is None else f'{sharpe:.2f}'}")


if __name__ == "__main__":
    main()