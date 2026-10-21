
import json

import duckdb
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama

from analytics import (
    calculate_max_drawdown as compute_max_drawdown,
    calculate_volatility as compute_volatility,
    get_price_history,
)
from pipeline import DB_PATH


@tool
def get_quality_report(ticker: str) -> str:
    """Summarize detected market data quality issues for a ticker."""

    ticker = ticker.upper()

    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        result = con.execute(
            """
            SELECT rule, severity, COUNT(*) AS count
            FROM quality_issues
            WHERE ticker = ?
            GROUP BY rule, severity
            ORDER BY count DESC
            """,
            [ticker],
        ).df()

    if result.empty:
        return f"No quality issues were detected for {ticker}."

    return result.to_json(orient="records")


@tool
def get_recent_anomalies(ticker: str = "ALL") -> str:
    """Return up to 20 recent flagged market data records."""

    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        if ticker.upper() == "ALL":
            result = con.execute(
                """
                SELECT ticker, date, rule, severity,
                       observed_value, details
                FROM quality_issues
                ORDER BY date DESC
                LIMIT 20
                """
            ).df()
        else:
            result = con.execute(
                """
                SELECT ticker, date, rule, severity,
                       observed_value, details
                FROM quality_issues
                WHERE ticker = ?
                ORDER BY date DESC
                LIMIT 20
                """,
                [ticker.upper()],
            ).df()

    if result.empty:
        return "No matching quality issues were found."

    return result.to_json(orient="records")


@tool
def get_price_summary(ticker: str) -> str:
    """Return the first and last available dates and prices for a ticker."""

    prices = get_price_history(ticker)

    if prices.empty:
        return f"No data found for {ticker}."

    prices = prices.dropna(subset=["adj_close"])

    if prices.empty:
        return f"No valid adjusted prices found for {ticker}."

    return json.dumps({
        "ticker": ticker.upper(),
        "observations": len(prices),
        "first_date": str(prices.iloc[0]["date"]),
        "last_date": str(prices.iloc[-1]["date"]),
        "first_adjusted_close": float(prices.iloc[0]["adj_close"]),
        "last_adjusted_close": float(prices.iloc[-1]["adj_close"]),
    })


@tool
def get_volatility(ticker: str, window: int = 20) -> str:
    """Calculate annualized volatility from recent daily adjusted returns."""

    result = compute_volatility(ticker, window)

    return json.dumps(result)


@tool
def get_max_drawdown(ticker: str) -> str:
    """Calculate the maximum drawdown over the available data history."""

    result = compute_max_drawdown(ticker)

    return json.dumps(result)


TOOLS = [
    get_quality_report,
    get_recent_anomalies,
    get_price_summary,
    get_volatility,
    get_max_drawdown,
]


model = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)

agent = create_agent(
    model=model,
    tools=TOOLS,
    system_prompt="""
You are a market data quality and quantitative analytics assistant.

Use the supplied tools to retrieve data and calculate metrics.
Never invent prices, dates, quality findings, or numerical results.

Distinguish detected anomalies from confirmed errors.
A large price movement may be legitimate and could be related to
a corporate action or market event.

Explain which data or tool result supports your answer.
If the database does not contain enough information, say so.
Do not give investment recommendations.
""",
)


def ask_agent(question: str) -> str:
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    answer = result["messages"][-1].content

    if isinstance(answer, str):
        return answer

    return str(answer)
