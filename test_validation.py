
import pandas as pd

from pipeline import validate_market_data


sample = pd.DataFrame([
    {
        "ticker": "TEST",
        "date": "2026-10-20",
        "open": 100.0,
        "high": 105.0,
        "low": 95.0,
        "close": 102.0,
        "adj_close": 102.0,
        "volume": 1000,
        "dividends": 0.0,
        "stock_splits": 0.0,
    },
    {
        "ticker": "TEST",
        "date": "2026-10-21",
        "open": 102.0,
        "high": 99.0,    # Intentionally invalid
        "low": 101.0,
        "close": 103.0,
        "adj_close": 103.0,
        "volume": 1200,
        "dividends": 0.0,
        "stock_splits": 0.0,
    },
])

issues = validate_market_data(sample)

print(issues.to_string(index=False))

assert "INVALID_OHLC" in issues["rule"].values

print("Validation test passed.")
