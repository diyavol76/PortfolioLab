import yfinance as yf
import pandas as pd
from typing import Optional


class YahooFinanceProvider:
    def get_stock_info(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return {
                "ticker": ticker,
                "name": info.get("longName", ticker),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
                "previous_close": info.get("previousClose", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "ev_ebitda": info.get("enterpriseToEbitda"),
                "roe": info.get("returnOnEquity"),
                "revenue": info.get("totalRevenue"),
                "ebitda": info.get("ebitda"),
                "net_income": info.get("netIncomeToCommon"),
                "free_cash_flow": info.get("freeCashflow"),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e), "current_price": 0}

    def get_historical_prices(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=period)
            if hist.empty:
                return pd.DataFrame(columns=["Date", "Close"])
            hist = hist.reset_index()[["Date", "Close"]]
            hist["Date"] = pd.to_datetime(hist["Date"]).dt.tz_localize(None)
            return hist
        except Exception:
            return pd.DataFrame(columns=["Date", "Close"])

    def get_financial_statements(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            income_stmt = t.financials
            balance_sheet = t.balance_sheet
            cash_flow = t.cashflow

            result = {}

            if income_stmt is not None and not income_stmt.empty:
                result["income_statement"] = income_stmt.to_dict()
            else:
                result["income_statement"] = {}

            if balance_sheet is not None and not balance_sheet.empty:
                result["balance_sheet"] = balance_sheet.to_dict()
            else:
                result["balance_sheet"] = {}

            if cash_flow is not None and not cash_flow.empty:
                result["cash_flow"] = cash_flow.to_dict()
            else:
                result["cash_flow"] = {}

            return result
        except Exception as e:
            return {"error": str(e), "income_statement": {}, "balance_sheet": {}, "cash_flow": {}}

    def get_multiple_prices(self, tickers: list, period: str = "1y") -> pd.DataFrame:
        if not tickers:
            return pd.DataFrame()
        try:
            data = yf.download(tickers, period=period, auto_adjust=True, progress=False)
            if data.empty:
                return pd.DataFrame()
            if len(tickers) == 1:
                close = data[["Close"]].copy()
                close.columns = tickers
            else:
                close = data["Close"].copy()
            close.index = pd.to_datetime(close.index).tz_localize(None)
            return close
        except Exception:
            return pd.DataFrame()
