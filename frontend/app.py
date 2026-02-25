import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="PortfolioLab",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def api_get(path: str, params: dict = None):
    try:
        resp = requests.get(f"{BACKEND_URL}{path}", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def api_post(path: str, data: dict):
    try:
        resp = requests.post(f"{BACKEND_URL}{path}", json=data, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def api_delete(path: str):
    try:
        resp = requests.delete(f"{BACKEND_URL}{path}", timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def check_backend():
    result = api_get("/")
    return result is not None


# Sidebar
st.sidebar.title("📈 PortfolioLab")
st.sidebar.divider()

backend_ok = check_backend()
if not backend_ok:
    st.error(
        f"⚠️ Cannot connect to backend at `{BACKEND_URL}`. "
        "Please start the FastAPI backend with:\n\n"
        "```\nuvicorn backend.main:app --reload\n```"
    )
    st.stop()

st.sidebar.success("✅ Backend connected")
st.sidebar.divider()

# Portfolio management
st.sidebar.subheader("Add Stock")
with st.sidebar.form("add_stock_form"):
    ticker_input = st.text_input("Ticker", placeholder="e.g. AAPL").upper()
    quantity_input = st.number_input("Quantity", min_value=0.01, step=1.0, value=10.0)
    cost_basis_input = st.number_input("Cost Basis (per share $)", min_value=0.01, step=1.0, value=100.0)
    submitted = st.form_submit_button("Add to Portfolio")
    if submitted and ticker_input:
        result = api_post("/api/portfolio/add", {
            "ticker": ticker_input,
            "quantity": quantity_input,
            "cost_basis": cost_basis_input,
        })
        if result:
            st.sidebar.success(f"Added {ticker_input}!")
            st.rerun()
        else:
            st.sidebar.error("Failed to add stock.")

# Current holdings
portfolio = api_get("/api/portfolio")
if portfolio and portfolio.get("items"):
    st.sidebar.divider()
    st.sidebar.subheader("Current Holdings")
    for item in portfolio["items"]:
        col_a, col_b = st.sidebar.columns([3, 1])
        col_a.write(f"**{item['ticker']}** — {item['quantity']} @ ${item['cost_basis']:.2f}")
        if col_b.button("✕", key=f"remove_{item['ticker']}"):
            api_delete(f"/api/portfolio/{item['ticker']}")
            st.rerun()

# Metrics ticker selector
st.sidebar.divider()
st.sidebar.subheader("Analyze Ticker")
analyze_ticker = st.sidebar.text_input("Ticker for metrics", value="AAPL").upper()

# Main content
st.title("📈 PortfolioLab — Financial Analysis Dashboard")

tab1, tab2, tab3 = st.tabs(["Portfolio Overview", "Financial Metrics", "Risk Analysis"])

with tab1:
    from frontend.dashboard.overview import render_overview
    with st.spinner("Loading portfolio data..."):
        portfolio_summary = api_get("/api/portfolio/summary")
        benchmark_data = api_get("/api/benchmark")
    render_overview(portfolio_summary, benchmark_data)

with tab2:
    from frontend.dashboard.metrics import render_metrics
    if analyze_ticker:
        with st.spinner(f"Loading metrics for {analyze_ticker}..."):
            metrics_data = api_get(f"/api/metrics/{analyze_ticker}")
        render_metrics(analyze_ticker, metrics_data)
    else:
        st.info("Enter a ticker in the sidebar to view financial metrics.")

with tab3:
    from frontend.dashboard.risk import render_risk
    with st.spinner("Loading risk data..."):
        risk_data = api_get("/api/risk")
        spy_prices = api_get("/api/prices/SPY")
    render_risk(risk_data, spy_prices)
