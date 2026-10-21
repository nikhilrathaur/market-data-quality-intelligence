# Market Data Quality & Intelligence Assistant

A local-first market data quality and quantitative analytics platform built with Python, DuckDB, Streamlit, LangChain, and Ollama.

The project combines market data ingestion, automated validation, quantitative analytics, and a local AI assistant to help investigate data-quality issues through a single interface.

## Overview

Market data is a critical input to portfolio valuation, quantitative research, and risk management. Missing observations, invalid prices, duplicate records, and unexplained movements can affect downstream analytics and investment decisions.

This project demonstrates a practical workflow for ingesting historical market data, validating its integrity, calculating quantitative metrics, and investigating anomalies using a locally running language model.

## Key Features

- **Market Data Ingestion** — Retrieve historical equity market data and normalize it into a consistent schema.
- **Automated Data Quality Checks** — Identify duplicate observations, missing prices, invalid OHLC relationships, non-positive prices, invalid volumes, and unusually large adjusted-price movements.
- **Quantitative Analytics** — Calculate historical returns, annualized volatility, and maximum drawdown.
- **Data Storage** — Store normalized market data and quality findings in DuckDB for efficient local querying.
- **Interactive Dashboard** — Explore market data, validation results, and quantitative metrics through Streamlit.
- **AI-Assisted Investigation** — Use a locally running language model through Ollama and LangChain to query summaries and investigate potential anomalies.
- **Local-First Architecture** — Run analytics and AI inference locally without requiring a paid LLM API.

## Architecture

```text
Historical Market Data
        |
        v
   Data Ingestion
        |
        v
 Normalization & Validation
        |
        +-------------------+
        |                   |
        v                   v
   Market Data         Quality Issues
        |                   |
        +---------+---------+
                  |
                  v
             DuckDB
                  |
          +-------+--------+
          |                |
          v                v
   Streamlit Dashboard  Analytics & AI Tools
                           |
                           v
                    Local Ollama Model
```

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Data processing | pandas, NumPy |
| Historical market data | yfinance |
| Analytical database | DuckDB |
| Dashboard | Streamlit |
| Visualization | Plotly |
| LLM orchestration | LangChain |
| Local model inference | Ollama |

## Data Quality Framework

The validation pipeline checks for common market data integrity issues, including:

- Duplicate ticker and date combinations.
- Missing OHLC price fields.
- Non-positive prices.
- Invalid relationships between open, high, low, and close prices.
- Missing or invalid trading volumes.
- Unusually large adjusted-price movements that may require investigation.

Potential anomalies are recorded for review rather than automatically assumed to be erroneous. Large price movements can reflect genuine market events, corporate actions, or data problems.

## Quantitative Analytics

The analytics module supports:

- **Historical Returns** — Calculate daily returns from adjusted closing prices.
- **Annualized Volatility** — Estimate realized volatility using daily returns and an annualization factor of 252 trading days.
- **Maximum Drawdown** — Measure the largest peak-to-trough decline over a selected observation period.
- **Data Quality Summaries** — Review validation issues and investigate affected observations.

These metrics provide a foundation for extending the project toward portfolio risk monitoring and more advanced quantitative research.

## AI-Assisted Investigation

The AI assistant uses LangChain to connect a local Ollama model with application-specific tools.

Depending on the available tools, users can ask questions about:

- Recent data-quality anomalies.
- Data-quality issue summaries.
- Price history and market movements.
- Historical volatility.
- Maximum drawdown.

The language model supports investigation and explanation; numerical results should be sourced from the underlying Python analytics and database rather than relying on the model to perform financial calculations independently.

## Getting Started

### Prerequisites

Install:

- Python 3.11 or a compatible Python version supported by the dependencies.
- [Git](https://git-scm.com/)
- [Ollama](https://ollama.com/)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/market-data-quality-intelligence.git
cd market-data-quality-intelligence
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the local language model

Pull the model used by the application:

```bash
ollama pull qwen2.5:3b
```

Ensure Ollama is running before using the AI investigation features.

### 5. Ingest and validate market data

Run the data pipeline:

```bash
python pipeline.py
```

This step should populate the local DuckDB database with normalized market data and validation findings.

### 6. Launch the dashboard

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## Project Structure

```text
market-data-quality-intelligence/
├── app.py              # Streamlit dashboard
├── pipeline.py         # Market data ingestion and validation
├── analytics.py        # Quantitative analytics
├── agent.py            # LangChain agent and investigation tools
├── requirements.txt    # Python dependencies
├── .gitignore          # Excluded files and local artifacts
└── README.md           # Project documentation
```

## Design Principles

- **Data integrity first:** Validate observations before using them in downstream analytics.
- **Separation of concerns:** Keep ingestion, validation, analytics, and presentation logically distinct.
- **Explainable findings:** Surface potential issues for review instead of silently altering source data.
- **Reproducibility:** Keep the pipeline and analytics logic in version-controlled source files.
- **Local execution:** Use a local database and language model to minimize external service dependencies.

## Limitations

- Historical data is sourced through `yfinance`, an unofficial interface to Yahoo Finance. Availability, coverage, adjustments, and historical values may change.
- The project is intended for learning, research, and demonstration purposes; it is not an institutional market data feed.
- Anomaly thresholds are configurable heuristics, not proof that an observation is incorrect.
- The AI assistant may produce inaccurate explanations. Verify findings against source data and deterministic analytics.
- The project does not currently represent a production risk-management or trading system.

## Future Enhancements

- Multi-vendor price reconciliation.
- Corporate-action-aware validation and adjustment checks.
- Exchange calendars and missing-trading-day detection.
- Data lineage, ingestion timestamps, and source-level audit trails.
- Configurable validation rules and severity classifications.
- Additional asset classes, including fixed income, FX, and derivatives.
- Automated regression tests and data-quality monitoring.
- Portfolio-level risk metrics and stress scenarios.

## Disclaimer

This project is for educational and portfolio demonstration purposes only. It is not investment advice and should not be used as the sole basis for trading, valuation, or risk-management decisions.
