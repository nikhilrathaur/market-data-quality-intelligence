
import duckdb
import numpy as np
import pandas as pd

from pipeline import DB_PATH


def get_price_history(ticker, start_date="", end_date=""):
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        query = """
            SELECT date, close, adj_close, volume
            FROM prices
            WHERE ticker = ?
        """
        params = [ticker.upper()]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date"

        return con.execute(query, params).df()


def calculate_volatility(ticker, window=20):
    if not 2 <= window <= 252:
        raise ValueError("Window must be between 2 and 252.")

    prices = get_price_history(ticker)

    if prices.empty:
        return {"error": f"No data found for {ticker}."}

    prices["daily_return"] = prices["adj_close"].pct_change()
    returns = prices["daily_return"].dropna()

    if len(returns) < window:
        return {"error": "Not enough observations for this window."}

    recent_returns = returns.tail(window)
    volatility = recent_returns.std(ddof=1) * np.sqrt(252)

    return {
        "ticker": ticker.upper(),
        "observations": len(recent_returns),
        "annualized_volatility": round(float(volatility), 4),
        "window": window,
    }


def calculate_max_drawdown(ticker):
    prices = get_price_history(ticker)

    if prices.empty:
        return {"error": f"No data found for {ticker}."}

    prices = prices.dropna(subset=["adj_close"]).copy()

    if prices.empty:
        return {"error": "No valid adjusted prices available."}

    running_peak = prices["adj_close"].cummax()
    drawdowns = prices["adj_close"] / running_peak - 1

    worst_index = drawdowns.idxmin()

    return {
        "ticker": ticker.upper(),
        "max_drawdown": round(float(drawdowns.min()), 4),
        "trough_date": str(prices.loc[worst_index, "date"]),
    }
