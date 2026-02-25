from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import pandas as pd

from backend.models.portfolio import Portfolio, PortfolioItem, AddStockRequest, PortfolioResponse
from backend.data.yahoo_finance import YahooFinanceProvider
from backend.services.portfolio_service import PortfolioService
from backend.services.financial_service import FinancialService
from backend.services.risk_service import RiskService

app = FastAPI(title="PortfolioLab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store
portfolio_store: Portfolio = Portfolio(name="My Portfolio", items=[])

yahoo = YahooFinanceProvider()
portfolio_svc = PortfolioService()
financial_svc = FinancialService()
risk_svc = RiskService()


@app.get("/")
def health_check():
    return {"status": "ok", "service": "PortfolioLab API"}


@app.get("/api/portfolio")
def get_portfolio():
    return {"name": portfolio_store.name, "items": [i.model_dump() for i in portfolio_store.items]}


@app.post("/api/portfolio/add")
def add_stock(request: AddStockRequest):
    ticker = request.ticker.upper()
    for item in portfolio_store.items:
        if item.ticker == ticker:
            # Update with weighted average cost basis
            total_qty = item.quantity + request.quantity
            item.cost_basis = (item.quantity * item.cost_basis + request.quantity * request.cost_basis) / total_qty
            item.quantity = total_qty
            return {"message": f"Updated {ticker}", "item": item.model_dump()}
    new_item = PortfolioItem(ticker=ticker, quantity=request.quantity, cost_basis=request.cost_basis)
    portfolio_store.items.append(new_item)
    return {"message": f"Added {ticker}", "item": new_item.model_dump()}


@app.delete("/api/portfolio/{ticker}")
def remove_stock(ticker: str):
    ticker = ticker.upper()
    original_len = len(portfolio_store.items)
    portfolio_store.items = [i for i in portfolio_store.items if i.ticker != ticker]
    if len(portfolio_store.items) == original_len:
        raise HTTPException(status_code=404, detail=f"{ticker} not found in portfolio")
    return {"message": f"Removed {ticker}"}


@app.get("/api/portfolio/summary", response_model=PortfolioResponse)
def portfolio_summary():
    if not portfolio_store.items:
        return PortfolioResponse(
            items=[],
            total_value=0.0,
            total_cost=0.0,
            total_return_pct=0.0,
            daily_return_pct=0.0,
        )

    tickers = [item.ticker for item in portfolio_store.items]
    prices = {}
    prev_prices = {}

    for ticker in tickers:
        info = yahoo.get_stock_info(ticker)
        prices[ticker] = info.get("current_price", 0)
        prev_prices[ticker] = info.get("previous_close", prices[ticker])

    total_value = sum(item.quantity * prices.get(item.ticker, 0) for item in portfolio_store.items)
    total_cost = sum(item.quantity * item.cost_basis for item in portfolio_store.items)
    total_return_pct = portfolio_svc.calculate_total_return(portfolio_store, prices)
    daily_return_pct = portfolio_svc.calculate_daily_return(portfolio_store, prices, prev_prices)

    return PortfolioResponse(
        items=portfolio_store.items,
        total_value=total_value,
        total_cost=total_cost,
        total_return_pct=total_return_pct,
        daily_return_pct=daily_return_pct,
    )


@app.get("/api/metrics/{ticker}")
def get_metrics(ticker: str):
    ticker = ticker.upper()
    metrics = financial_svc.get_summary_metrics(ticker)
    return metrics


@app.get("/api/risk")
def get_risk():
    if not portfolio_store.items:
        return {"volatility": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0, "correlation_matrix": {}}

    tickers = [item.ticker for item in portfolio_store.items]
    price_data = yahoo.get_multiple_prices(tickers, period="1y")
    risk_metrics = risk_svc.calculate_portfolio_risk(portfolio_store, price_data)
    return risk_metrics


@app.get("/api/prices/{ticker}")
def get_prices(ticker: str, period: str = "1y"):
    ticker = ticker.upper()
    hist = yahoo.get_historical_prices(ticker, period=period)
    if hist.empty:
        return {"ticker": ticker, "prices": []}
    records = hist.to_dict(orient="records")
    for r in records:
        if hasattr(r.get("Date"), "isoformat"):
            r["Date"] = r["Date"].isoformat()
    return {"ticker": ticker, "prices": records}


@app.get("/api/benchmark")
def get_benchmark(period: str = "1y"):
    hist = yahoo.get_historical_prices("SPY", period=period)
    if hist.empty:
        return {"ticker": "SPY", "prices": []}
    records = hist.to_dict(orient="records")
    for r in records:
        if hasattr(r.get("Date"), "isoformat"):
            r["Date"] = r["Date"].isoformat()
    return {"ticker": "SPY", "prices": records}
