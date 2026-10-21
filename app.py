
import duckdb
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from agent import ask_agent
from pipeline import DB_PATH, run_pipeline


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="MarketPulse | Data Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM DESIGN SYSTEM
# --------------------------------------------------

st.markdown("""
<style>
@import url(
'https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700;800&display=swap'
);

:root {
    --bg: #0b1120;
    --panel: #151f32;
    --panel-light: #1b2840;
    --border: #29364b;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --green: #22c55e;
    --amber: #fbbf24;
    --red: #f87171;
}

.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(11, 17, 32, 0.95);
}

[data-testid="stSidebar"] {
    background: #0e1728;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: var(--text) !important;
    letter-spacing: -0.035em;
}

p, label {
    color: #cbd5e1;
}

[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 13px;
    padding: 18px 20px;
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'DM Mono', monospace;
}

.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
}

.eyebrow {
    color: var(--green);
    text-transform: uppercase;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.13em;
    margin-bottom: 8px;
}

.brand {
    font-size: 1.28rem;
    font-weight: 800;
    letter-spacing: -0.05em;
    color: #f8fafc;
}

.brand span {
    color: var(--green);
}

.subtitle {
    color: var(--muted);
    font-size: 0.84rem;
    margin-top: 5px;
}

.pill {
    display: inline-block;
    background: rgba(34,197,94,0.12);
    color: #4ade80;
    border: 1px solid rgba(34,197,94,0.3);
    padding: 4px 9px;
    border-radius: 30px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
}

div.stButton > button {
    border-radius: 9px;
    border: 1px solid var(--border);
    background: var(--panel-light);
    color: var(--text);
    font-weight: 600;
    min-height: 42px;
    transition: 0.15s ease;
}

div.stButton > button:hover {
    border-color: var(--green);
    color: var(--green);
}

div.stButton > button[kind="primary"] {
    background: var(--green);
    color: #052e16;
    border-color: var(--green);
}

[data-testid="stChatMessage"] {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 10px;
}

[data-testid="stChatInput"] {
    border-color: var(--border);
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 10px;
}

hr {
    border-color: var(--border);
}

footer {
    visibility: hidden;
}

/* Keep the page heading clear of the top bar */
.block-container {
    padding-top: 3rem !important;
}

/* Ensure the main heading has enough breathing room */
.page-header {
    margin-top: 1.5rem !important;
    padding-top: 0.5rem !important;
    position: relative;
    z-index: 1;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DATABASE HELPERS
# --------------------------------------------------

def load_table(query, params=None):
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        return con.execute(query, params or []).df()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="brand">MARKET<span>PULSE</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">Market data intelligence terminal</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    page = st.radio(
        "WORKSPACE",
        [
            "Overview",
            "Data Quality",
            "Quant Analytics",
            "AI Investigation",
        ],
        label_visibility="visible",
    )

    st.divider()

    st.markdown("#### DATA CONTROLS")

    if st.button("↻  Refresh market data", use_container_width=True):
        with st.spinner("Downloading and validating..."):
            try:
                run_pipeline()
                st.success("Refresh completed.")
                st.rerun()
            except Exception as error:
                st.error(f"Refresh failed: {error}")

    st.caption("Data source: Yahoo Finance via yfinance")
    st.caption("Storage: Local DuckDB")
    st.caption("AI: Local Ollama model")

    st.divider()

    st.markdown(
        '<span class="pill">● LOCAL WORKSPACE</span>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# LOAD DATABASE
# --------------------------------------------------

st.markdown(
    '<div class="eyebrow">QUANTITATIVE DATA OPERATIONS</div>',
    unsafe_allow_html=True,
)

st.markdown("# Market Data Intelligence")

st.markdown(
    '<div class="subtitle">'
    'Monitor market data integrity, investigate anomalies, '
    'and explore quantitative signals.'
    '</div>',
    unsafe_allow_html=True,
)

st.write("")

if not DB_PATH.exists():
    st.warning(
        "No database found. Run `python pipeline.py` "
        "in Terminal, then refresh this page."
    )
    st.stop()

try:
    prices = load_table("SELECT * FROM prices ORDER BY date")

    issues = load_table("""
        SELECT ticker, date, rule, severity,
               observed_value, details
        FROM quality_issues
        ORDER BY date DESC
    """)

except Exception as error:
    st.error(f"Unable to read the database: {error}")
    st.stop()

if prices.empty:
    st.warning("No price records are available.")
    st.stop()

tickers = sorted(prices["ticker"].dropna().unique().tolist())

if not tickers:
    st.warning("No valid ticker identifiers are available.")
    st.stop()

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = tickers[0]

if st.session_state.selected_ticker not in tickers:
    st.session_state.selected_ticker = tickers[0]


# --------------------------------------------------
# SECURITY SELECTOR
# --------------------------------------------------

selector_col, date_col = st.columns([2, 3])

with selector_col:
    ticker = st.selectbox(
        "SELECT SECURITY",
        tickers,
        key="selected_ticker",
    )

selected_prices = prices[
    prices["ticker"] == ticker
].copy()

selected_prices["date"] = pd.to_datetime(
    selected_prices["date"], errors="coerce"
)

selected_prices = selected_prices.dropna(subset=["date"])
selected_prices = selected_prices.sort_values("date")

selected_issues = issues[
    issues["ticker"] == ticker
].copy()

with date_col:
    st.markdown(
        f"""
        <div style="padding-top:30px; text-align:right">
            <span class="pill">HISTORICAL DATA</span>
            &nbsp;
            <span style="color:#94a3b8; font-size:0.8rem">
                {selected_prices["date"].min().strftime("%d %b %Y")}
                —
                {selected_prices["date"].max().strftime("%d %b %Y")}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# GLOBAL KPI CARDS
# --------------------------------------------------

st.write("")

total_records = len(prices)
total_issues = len(issues)
high_issues = (
    int((issues["severity"] == "HIGH").sum())
    if not issues.empty else 0
)
security_count = prices["ticker"].nunique()

k1, k2, k3, k4 = st.columns(4)

k1.metric("PRICE RECORDS", f"{total_records:,}")
k2.metric("SECURITIES", f"{security_count:,}")
k3.metric("QUALITY FLAGS", f"{total_issues:,}")
k4.metric("HIGH SEVERITY", f"{high_issues:,}")


# --------------------------------------------------
# PRICE CHART
# --------------------------------------------------

if page in ["Overview", "Quant Analytics"]:
    st.write("")

    left, right = st.columns([2.1, 1])

    with left:
        st.markdown(
            '<div class="eyebrow">01 / MARKET MONITOR</div>',
            unsafe_allow_html=True,
        )
        st.subheader(f"{ticker} · Price history")

        chart_prices = selected_prices.copy()

        price_field = st.radio(
            "PRICE SERIES",
            ["Adjusted close", "Close"],
            horizontal=True,
            label_visibility="collapsed",
            key="price_field",
        )

        column = (
            "adj_close"
            if price_field == "Adjusted close"
            else "close"
        )

        chart_prices[column] = pd.to_numeric(
            chart_prices[column], errors="coerce"
        )
        chart_prices = chart_prices.dropna(subset=[column])

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=chart_prices["date"],
                y=chart_prices[column],
                mode="lines",
                name=price_field,
                line=dict(color="#22c55e", width=2),
                fill="tozeroy",
                fillcolor="rgba(34,197,94,0.06)",
                hovertemplate=(
                    "%{x|%d %b %Y}<br>"
                    "Price: %{y:.2f}<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            height=340,
            margin=dict(l=5, r=5, t=15, b=5),
            paper_bgcolor="#151f32",
            plot_bgcolor="#151f32",
            font=dict(color="#94a3b8", size=11),
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#29364b",
                zeroline=False,
                title=None,
            ),
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown(
            '<div class="eyebrow">02 / QUALITY MONITOR</div>',
            unsafe_allow_html=True,
        )
        st.subheader("Issue summary")

        if selected_issues.empty:
            st.success("No issues flagged.")
        else:
            issue_counts = (
                selected_issues.groupby("rule")
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=True)
            )

            issue_fig = go.Figure(
                go.Bar(
                    x=issue_counts["count"],
                    y=issue_counts["rule"],
                    orientation="h",
                    marker_color="#fbbf24",
                    hovertemplate=(
                        "%{y}<br>Count: %{x}<extra></extra>"
                    ),
                )
            )

            issue_fig.update_layout(
                height=300,
                margin=dict(l=0, r=5, t=10, b=5),
                paper_bgcolor="#151f32",
                plot_bgcolor="#151f32",
                font=dict(color="#cbd5e1", size=10),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="#29364b",
                    title=None,
                ),
                yaxis=dict(title=None),
            )

            st.plotly_chart(
                issue_fig,
                use_container_width=True,
            )

    st.write("")

    st.markdown(
        '<div class="eyebrow">03 / RECENT FINDINGS</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Latest flagged records")

    if selected_issues.empty:
        st.info("No issues to display for this security.")
    else:
        st.dataframe(
            selected_issues.head(15),
            use_container_width=True,
            hide_index=True,
        )


# --------------------------------------------------
# DATA QUALITY WORKSPACE
# --------------------------------------------------

if page == "Data Quality":
    st.markdown(
        '<div class="eyebrow">VALIDATION WORKSPACE</div>',
        unsafe_allow_html=True,
    )
    st.subheader(f"Data quality · {ticker}")

    if selected_issues.empty:
        st.success("No quality issues detected for this security.")
    else:
        rule_options = sorted(
            selected_issues["rule"].dropna().unique().tolist()
        )

        chosen_rules = st.multiselect(
            "Filter by validation rule",
            rule_options,
            default=rule_options,
        )

        filtered = selected_issues[
            selected_issues["rule"].isin(chosen_rules)
        ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("#### Full issue distribution")

    if issues.empty:
        st.info("The database contains no flagged records.")
    else:
        st.dataframe(
            issues,
            use_container_width=True,
            hide_index=True,
        )


# --------------------------------------------------
# QUANT ANALYTICS WORKSPACE
# --------------------------------------------------

if page == "Quant Analytics":
    st.markdown(
        '<div class="eyebrow">QUANTITATIVE ANALYTICS</div>',
        unsafe_allow_html=True,
    )
    st.subheader(f"Risk and return metrics · {ticker}")

    from analytics import (
        calculate_max_drawdown,
        calculate_volatility,
    )

    window = st.slider(
        "Rolling volatility window (trading observations)",
        min_value=5,
        max_value=100,
        value=20,
    )

    vol_result = calculate_volatility(ticker, window)
    dd_result = calculate_max_drawdown(ticker)

    a, b = st.columns(2)

    with a:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.caption("ANNUALIZED VOLATILITY")

        if "error" in vol_result:
            st.warning(vol_result["error"])
        else:
            st.markdown(
                f'<div style="font-size:2rem; font-weight:700; '
                f'color:#22c55e">'
                f'{vol_result["annualized_volatility"]:.2%}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                f'Based on {vol_result["observations"]} daily '
                f'return observations.'
            )

        st.markdown('</div>', unsafe_allow_html=True)

    with b:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.caption("MAXIMUM DRAWDOWN")

        if "error" in dd_result:
            st.warning(dd_result["error"])
        else:
            st.markdown(
                f'<div style="font-size:2rem; font-weight:700; '
                f'color:#f87171">'
                f'{dd_result["max_drawdown"]:.2%}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                f'Trough date: {dd_result["trough_date"]}'
            )

        st.markdown('</div>', unsafe_allow_html=True)

    st.caption(
        "Metrics use the available stored historical series. "
        "Volatility is annualized using a 252-session convention."
    )


# --------------------------------------------------
# AI INVESTIGATION WORKSPACE
# --------------------------------------------------

if page in ["Overview", "AI Investigation"]:
    st.write("")
    st.markdown(
        '<div class="eyebrow">04 / AI INVESTIGATION DESK</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Investigate your market data")

    st.markdown(
        "Ask questions about quality flags, historical prices, "
        "volatility, or drawdown. The assistant uses predefined "
        "Python tools to retrieve results."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    prompts = [
        f"Summarize the quality issues for {ticker}.",
        f"Calculate the 20-day volatility for {ticker}.",
        f"Explain the maximum drawdown for {ticker}.",
    ]

    prompt_cols = st.columns(3)

    for index, prompt in enumerate(prompts):
        if prompt_cols[index].button(
            prompt,
            key=f"prompt_{index}_{ticker}",
            use_container_width=True,
        ):
            st.session_state.pending_question = prompt

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask a question about your market data..."
    )

    pending = st.session_state.pop(
        "pending_question", None
    )

    question = pending or question

    if question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Investigating..."):
                try:
                    answer = ask_agent(question)
                except Exception as error:
                    answer = (
                        "The assistant could not complete the "
                        f"request: {error}"
                    )

                st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
        })


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    '<div style="color:#64748b; font-size:0.75rem; '
    'text-align:center">'
    'MARKETPULSE · EDUCATIONAL PROTOTYPE · '
    'HISTORICAL DATA MAY BE INCOMPLETE OR DELAYED'
    '</div>',
    unsafe_allow_html=True,
)
