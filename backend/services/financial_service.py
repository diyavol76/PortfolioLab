import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, List, Tuple


class FinancialService:
    def _get_financials(self, ticker: str):
        try:
            t = yf.Ticker(ticker)
            return t
        except Exception:
            return None

    def revenue_growth_yoy(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            inc = t.financials
            if inc is None or inc.empty:
                return None
            revenue_row = None
            for label in ["Total Revenue", "Revenue"]:
                if label in inc.index:
                    revenue_row = inc.loc[label]
                    break
            if revenue_row is None or len(revenue_row) < 2:
                return None
            rev_sorted = revenue_row.sort_index(ascending=False)
            latest = rev_sorted.iloc[0]
            prior = rev_sorted.iloc[1]
            if prior == 0:
                return None
            return ((latest - prior) / abs(prior)) * 100
        except Exception:
            return None

    def revenue_growth_3y(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            inc = t.financials
            if inc is None or inc.empty:
                return None
            revenue_row = None
            for label in ["Total Revenue", "Revenue"]:
                if label in inc.index:
                    revenue_row = inc.loc[label]
                    break
            if revenue_row is None or len(revenue_row) < 4:
                return None
            rev_sorted = revenue_row.sort_index(ascending=False)
            latest = rev_sorted.iloc[0]
            oldest = rev_sorted.iloc[3]
            if oldest <= 0:
                return None
            return ((latest / oldest) ** (1 / 3) - 1) * 100
        except Exception:
            return None

    def ebitda_margin(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            ebitda = info.get("ebitda")
            revenue = info.get("totalRevenue")
            if ebitda and revenue and revenue != 0:
                return (ebitda / revenue) * 100
            return None
        except Exception:
            return None

    def net_income_margin(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            net_income = info.get("netIncomeToCommon")
            revenue = info.get("totalRevenue")
            if net_income is not None and revenue and revenue != 0:
                return (net_income / revenue) * 100
            return None
        except Exception:
            return None

    def roe(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            roe_val = info.get("returnOnEquity")
            if roe_val is not None:
                return roe_val * 100
            return None
        except Exception:
            return None

    def pe_ratio(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return info.get("trailingPE")
        except Exception:
            return None

    def ev_ebitda(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return info.get("enterpriseToEbitda")
        except Exception:
            return None

    def peg_ratio(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return info.get("pegRatio")
        except Exception:
            return None

    def free_cash_flow_trend(self, ticker: str) -> List[Tuple[str, float]]:
        try:
            t = yf.Ticker(ticker)
            cf = t.cashflow
            if cf is None or cf.empty:
                return []
            fcf_row = None
            for label in ["Free Cash Flow", "FreeCashFlow"]:
                if label in cf.index:
                    fcf_row = cf.loc[label]
                    break
            if fcf_row is None:
                # Try to compute: Operating Cash Flow - CapEx
                ocf_row = None
                capex_row = None
                for label in ["Operating Cash Flow", "Total Cash From Operating Activities"]:
                    if label in cf.index:
                        ocf_row = cf.loc[label]
                        break
                for label in ["Capital Expenditure", "Capital Expenditures"]:
                    if label in cf.index:
                        capex_row = cf.loc[label]
                        break
                if ocf_row is not None and capex_row is not None:
                    fcf_row = ocf_row + capex_row
                else:
                    return []
            result = []
            for date, val in fcf_row.sort_index().items():
                if pd.notna(val):
                    year = str(date.year) if hasattr(date, "year") else str(date)
                    result.append((year, float(val)))
            return result
        except Exception:
            return []

    def get_summary_metrics(self, ticker: str) -> dict:
        return {
            "ticker": ticker,
            "pe_ratio": self.pe_ratio(ticker),
            "ev_ebitda": self.ev_ebitda(ticker),
            "peg_ratio": self.peg_ratio(ticker),
            "roe": self.roe(ticker),
            "ebitda_margin": self.ebitda_margin(ticker),
            "net_income_margin": self.net_income_margin(ticker),
            "revenue_growth_yoy": self.revenue_growth_yoy(ticker),
            "revenue_growth_3y": self.revenue_growth_3y(ticker),
            "free_cash_flow_trend": self.free_cash_flow_trend(ticker),
        }
