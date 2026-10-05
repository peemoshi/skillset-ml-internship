import pytest

from risk import (
    InputError,
    annualized_volatility,
    daily_returns,
    load_prices,
    main,
    max_drawdown,
    sharpe_ratio,
    total_return,
)


VALID_CSV = (
    "date,price\n"
    "2024-01-01,100\n"
    "2024-01-02,102\n"
    "2024-01-03,99\n"
    "2024-01-04,105\n"
    "2024-01-05,103\n"
)


def write_csv(tmp_path, contents):
    path = tmp_path / "prices.csv"
    path.write_text(contents, encoding="utf-8")
    return path


def test_metrics_for_two_returns():
    prices = [100, 110, 99]
    returns = [0.1, -0.1]

    assert total_return(prices) == pytest.approx(-0.01, rel=1e-6, abs=1e-9)
    assert max_drawdown(prices) == pytest.approx(0.1, rel=1e-6, abs=1e-9)
    assert daily_returns(prices) == pytest.approx(returns, rel=1e-6, abs=1e-9)
    assert annualized_volatility(returns) == pytest.approx(2.2449944, rel=1e-6, abs=1e-9)
    assert sharpe_ratio(returns, rf=0.0) == pytest.approx(0.0, rel=1e-6, abs=1e-9)
    assert sharpe_ratio(returns, rf=0.0252) == pytest.approx(-0.0112249722, rel=1e-6, abs=1e-9)


def test_metrics_for_five_prices():
    prices = [100, 102, 99, 105, 103]
    returns = daily_returns(prices)

    assert total_return(prices) == pytest.approx(0.03, rel=1e-6, abs=1e-9)
    assert max_drawdown(prices) == pytest.approx(0.0294117647, rel=1e-6, abs=1e-9)
    assert annualized_volatility(returns) == pytest.approx(0.6508294, rel=1e-6, abs=1e-9)
    assert sharpe_ratio(returns, rf=0.0) == pytest.approx(3.1117842, rel=1e-6, abs=1e-9)
    assert sharpe_ratio(returns, rf=0.02) == pytest.approx(3.0810542, rel=1e-6, abs=1e-9)


def test_steady_growth_has_no_sharpe_ratio():
    prices = [100, 110, 121]

    assert max_drawdown(prices) == pytest.approx(0.0, rel=1e-6, abs=1e-9)
    assert sharpe_ratio(daily_returns(prices), rf=0.0) is None


def test_loads_valid_prices(tmp_path):
    path = write_csv(tmp_path, VALID_CSV)

    assert load_prices(path) == pytest.approx(
        [100.0, 102.0, 99.0, 105.0, 103.0], rel=1e-6, abs=1e-9
    )


def test_loads_utf8_bom_file(tmp_path):
    path = tmp_path / "prices.csv"
    path.write_bytes(b"\xef\xbb\xbf" + VALID_CSV.encode("utf-8"))

    assert load_prices(path) == pytest.approx(
        [100.0, 102.0, 99.0, 105.0, 103.0], rel=1e-6, abs=1e-9
    )


def test_ignores_blank_lines_at_end(tmp_path):
    path = write_csv(tmp_path, VALID_CSV + "\n\n")

    assert load_prices(path) == pytest.approx(
        [100.0, 102.0, 99.0, 105.0, 103.0], rel=1e-6, abs=1e-9
    )


def test_rejects_blank_line_between_data_rows(tmp_path):
    contents = "date,price\n2024-01-01,100\n\n2024-01-02,102\n2024-01-03,99\n"
    path = write_csv(tmp_path, contents)

    with pytest.raises(InputError, match="blank row"):
        load_prices(path)


@pytest.mark.parametrize(
    ("contents", "case"),
    [
        (None, "missing_file"),
        ("day,close\n2024-01-01,100\n2024-01-02,102\n2024-01-03,99\n", "wrong_header"),
        ("date,price\n2024-01-01,100\n2024-01-02,nope\n2024-01-03,99\n", "non_numeric_price"),
        ("date,price\n2024-01-01,100\n2024-01-02,0\n2024-01-03,99\n", "zero_price"),
        ("date,price\n2024-01-01,100\n2024-01-02,-1\n2024-01-03,99\n", "negative_price"),
        ("date,price\nnot-a-date,100\n2024-01-02,102\n2024-01-03,99\n", "bad_date"),
        ("date,price\n2024-01-01,100\n2024-01-01,102\n2024-01-03,99\n", "duplicate_date"),
        ("date,price\n2024-01-02,100\n2024-01-01,102\n2024-01-03,99\n", "out_of_order"),
        ("date,price\n2024-01-01,100\n2024-01-02,102\n", "two_data_rows"),
    ],
    ids=[
        "missing_file",
        "wrong_header",
        "non_numeric_price",
        "zero_price",
        "negative_price",
        "bad_date",
        "duplicate_date",
        "out_of_order",
        "two_data_rows",
    ],
)
def test_load_prices_rejects_invalid_input(tmp_path, contents, case):
    path = tmp_path / f"{case}.csv"
    if contents is not None:
        path.write_text(contents, encoding="utf-8")

    with pytest.raises(InputError):
        load_prices(path)


def test_main_prints_observations(tmp_path, capsys):
    path = write_csv(tmp_path, VALID_CSV)

    main([str(path)])

    assert capsys.readouterr().out.splitlines()[0].startswith("observations: 5")


def test_main_reports_invalid_file(tmp_path, capsys):
    path = write_csv(tmp_path, "not,a,valid,header\n")

    with pytest.raises(SystemExit) as exc_info:
        main([str(path)])

    assert exc_info.value.code == 1
    assert capsys.readouterr().err.startswith("error:")


@pytest.mark.parametrize("risk_free_rate", ["-0.5", "abc"])
def test_main_rejects_invalid_risk_free_rate(tmp_path, capsys, risk_free_rate):
    path = write_csv(tmp_path, VALID_CSV)

    with pytest.raises(SystemExit) as exc_info:
        main([str(path), "--rf", risk_free_rate])

    assert exc_info.value.code == 1
    assert capsys.readouterr().err.startswith("error:")


def test_main_reports_extreme_price_changes(tmp_path, capsys):
    contents = "date,price\n2024-01-01,1e-300\n2024-01-02,1e300\n2024-01-03,1e-300\n"
    path = write_csv(tmp_path, contents)

    with pytest.raises(SystemExit) as exc_info:
        main([str(path)])

    error = capsys.readouterr().err
    assert exc_info.value.code == 1
    assert error.startswith("error:")
    assert "Traceback" not in error