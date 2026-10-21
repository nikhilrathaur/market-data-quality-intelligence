
from pathlib import Path

import duckdb
import pandas as pd
import yfinance as yf

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "market_data.duckdb"

TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]

PRICE_COLUMNS = [
    "ticker",
    "date",
    "open",
    "high",
    "low",
    "close",
    "adj_close",
    "volume",
    "dividends",
    "stock_splits",
]

ISSUE_COLUMNS = [
    "ticker",
    "date",
    "rule",
    "severity",
    "observed_value",
    "details",
]


def download_market_data():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    all_prices = []

    for ticker in TICKERS:
        print(f"Downloading {ticker}...")

        history = yf.Ticker(ticker).history(
            period="1y",
            interval="1d",
            auto_adjust=False,
            actions=True,
        )

        if history.empty:
            print(f"No data returned for {ticker}")
            continue

        # Preserve the original download for inspection.
        history.to_csv(RAW_DIR / f"{ticker}.csv")

        # Convert the downloaded data into a standard format.
        history = history.reset_index()
        history.columns = [
            str(column).strip().lower().replace(" ", "_")
            for column in history.columns
        ]

        history = history.rename(
            columns={
                "stock_splits": "stock_splits",
                "adj_close": "adj_close",
            }
        )

        if "datetime" in history.columns:
            history = history.rename(
                columns={"datetime": "date"}
            )

        history["date"] = (
            pd.to_datetime(history["date"], utc=True)
            .dt.strftime("%Y-%m-%d")
        )

        history["ticker"] = ticker

        # Ensure every expected column exists.
        for column in PRICE_COLUMNS:
            if column not in history.columns:
                history[column] = None

        history = history[PRICE_COLUMNS]

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "adj_close",
            "volume",
            "dividends",
            "stock_splits",
        ]

        for column in numeric_columns:
            history[column] = pd.to_numeric(
                history[column], errors="coerce"
            )

        all_prices.append(history)

    if not all_prices:
        raise RuntimeError(
            "No market data downloaded. Check your connection "
            "and try again."
        )

    prices = pd.concat(all_prices, ignore_index=True)

    print(f"Downloaded {len(prices)} price records.")
    return prices



def validate_market_data(prices):
    issues = []

    # Check for duplicate ticker/date records.
    duplicate_mask = prices.duplicated(
        subset=["ticker", "date"],
        keep=False,
    )

    for _, row in prices[duplicate_mask].iterrows():
        issues.append({
            "ticker": row["ticker"],
            "date": row["date"],
            "rule": "DUPLICATE_RECORD",
            "severity": "HIGH",
            "observed_value": str(row["close"]),
            "details": (
                "More than one record exists for this "
                "ticker and date."
            ),
        })

    # Check every price record.
    for _, row in prices.iterrows():
        ticker = row["ticker"]
        date = row["date"]

        o = row["open"]
        h = row["high"]
        l = row["low"]
        c = row["close"]

        # OHLC fields should be populated.
        if any(pd.isna(value) for value in [o, h, l, c]):
            issues.append({
                "ticker": ticker,
                "date": date,
                "rule": "MISSING_OHLC",
                "severity": "HIGH",
                "observed_value": None,
                "details": "One or more OHLC fields are missing.",
            })
            continue

        # Prices should be positive.
        if min(o, h, l, c) <= 0:
            issues.append({
                "ticker": ticker,
                "date": date,
                "rule": "NON_POSITIVE_PRICE",
                "severity": "HIGH",
                "observed_value": str(c),
                "details": "An OHLC price is zero or negative.",
            })

        # High must be at least as high as open and close.
        # Low must be at most as low as open and close.
        if h < max(o, c, l) or l > min(o, c, h):
            issues.append({
                "ticker": ticker,
                "date": date,
                "rule": "INVALID_OHLC",
                "severity": "HIGH",
                "observed_value": (
                    f"O={o}, H={h}, L={l}, C={c}"
                ),
                "details": (
                    "The OHLC values violate price-range "
                    "consistency rules."
                ),
            })

        if pd.isna(row["volume"]) or row["volume"] < 0:
            issues.append({
                "ticker": ticker,
                "date": date,
                "rule": "INVALID_VOLUME",
                "severity": "MEDIUM",
                "observed_value": str(row["volume"]),
                "details": "Volume is missing or negative.",
            })

    # Large close-to-close moves are suspicious, not
    # automatically incorrect.
    ordered = prices.sort_values(["ticker", "date"]).copy()

    ordered["daily_return"] = (
        ordered.groupby("ticker")["adj_close"].pct_change()
    )

    outliers = ordered[
        ordered["daily_return"].abs() > 0.10
    ]

    for _, row in outliers.iterrows():
        issues.append({
            "ticker": row["ticker"],
            "date": row["date"],
            "rule": "LARGE_DAILY_RETURN",
            "severity": "MEDIUM",
            "observed_value": round(
                float(row["daily_return"]), 4
            ),
            "details": (
                "Adjusted close moved by more than 10%. "
                "Investigate the market event and data."
            ),
        })

    return pd.DataFrame(issues, columns=ISSUE_COLUMNS)


def save_to_database(prices, issues):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(DB_PATH)) as connection:
        connection.register("incoming_prices", prices)
        connection.execute("""
            CREATE OR REPLACE TABLE prices AS
            SELECT * FROM incoming_prices
        """)
        connection.unregister("incoming_prices")

        connection.register("incoming_issues", issues)
        connection.execute("""
            CREATE OR REPLACE TABLE quality_issues AS
            SELECT * FROM incoming_issues
        """)
        connection.unregister("incoming_issues")

    print(f"Database saved at: {DB_PATH}")
    print(f"Price records: {len(prices)}")
    print(f"Quality issues: {len(issues)}")


def run_pipeline():
    prices = download_market_data()
    issues = validate_market_data(prices)
    save_to_database(prices, issues)

    print("\nIssue counts:")
    if issues.empty:
        print("No quality issues detected.")
    else:
        print(issues["rule"].value_counts().to_string())


if __name__ == "__main__":
    run_pipeline()