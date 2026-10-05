# Audit Notes - Portfolio Risk CLI

Small command-line tool: reads daily prices for one asset from a CSV and prints total return, annualized volatility, max drawdown and Sharpe ratio. Standard library only; tests in pytest.

## Process

1. Wrote `SPEC.md` first (inputs, definitions, error handling, out-of-scope) before asking an AI for code.
2. Asked an AI assistant to generate `risk.py` to my spec and architecture (small pure functions, one `InputError`, validation separate from the maths). The untouched original is kept as `risk_ai_original.py`.
3. Reviewed the code before running it, then ran it on edge-case inputs. Each problem found was reproduced on my machine, fixed with a narrow AI prompt ("change nothing else"), applied by hand, and re-checked.
4. Had the AI write `test_risk.py` against expected values I supplied, computed independently of the program's own code (NumPy cross-check, plus one case verified by hand).

## What the AI generated and I accepted

- Overall structure, argument parsing, and the maths functions (returns, volatility, drawdown, Sharpe) matched the spec.
- Validation of header, dates, prices, `--rf`, missing files, directories and non-UTF-8 files; clear `error:` messages with exit code 1.
- No security-sensitive logic: no secrets, no `eval` or shell calls, no network, read-only file access. Error messages only echo values that were validated or the path the user typed.

## Problems found and corrected

| # | Problem | How found | Fix | Check |
|---|---|---|---|---|
| 1 | Steady 10% daily growth printed a Sharpe of about 1.2e16. Float rounding made the standard deviation about 1e-16, so `stdev == 0` never fired. | Review plus edge-case run | Zero-volatility tolerance of 1e-12 (float noise is about 1e-16; real daily moves are far larger) | Prints `n/a`; `sample_prices.csv` still 3.11; regression test |
| 2 | CSV saved by Excel as "CSV UTF-8" rejected with a misleading header error (invisible byte-order mark) | Review | Read file with a BOM-tolerant encoding | File loads; regression test |
| 3 | One harmless blank line at end of file rejected | Review (spec was strict) | Decision: ignore blank lines at end of file only; a blank row between data rows is still an error. `SPEC.md` updated to match | End-of-file case loads, middle case still errors; two tests |
| 4 | Extreme prices (1e-300 then 1e300) overflowed and crashed with a Python traceback, against the spec | Edge-case run | Check every daily return is finite; raise `InputError` handled in `main()`. The first fix attempt had to make sure the check ran inside the `try` block | Clean `error:` message, exit code 1; regression test |

## Review checklist

- **Imports:** all used, standard library only.
- **Error handling:** expected input errors go through one path; problem 4 was the one gap.
- **Security-sensitive logic:** none (see above).
- **Duplication:** `parse_date` and `parse_price` repeat the same try/except pattern. Left as is; clear enough at this size.
- **Assumptions:** 252 trading days per year; simple (not log) returns; sample standard deviation; no check for gaps between dates, so the tool assumes the data is daily.

## Known limitations (accepted, not fixed)

- `float()` accepts forms like `1_000` and ` 1010 ` as valid prices.
- The whole file is read into memory (fine for this size).
- Tests do not yet check the printed percentages in `main()`, a valid non-zero `--rf` end to end, or an empty file.

## Verification

`pytest -v`: 21 passed. Expected values were hardcoded from an independent calculation, not copied from the program's formulas.