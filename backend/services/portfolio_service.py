import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from backend.models.portfolio import Portfolio, PortfolioItem


class PortfolioService:
    def calculate_current_value(self, portfolio: Portfolio, prices: Dict[str, float]) -> Dict[str, float]:
        values = {}
        for item in portfolio.items:
            price = prices.get(item.ticker, 0)
            values[item.ticker] = item.quantity * price
        return values

    def calculate_total_return(self, portfolio: Portfolio, prices: Dict[str, float]) -> float:
        total_value = 0.0
        total_cost = 0.0
        for item in portfolio.items:
            price = prices.get(item.ticker, 0)
            total_value += item.quantity * price
            total_cost += item.quantity * item.cost_basis
        if total_cost == 0:
            return 0.0
        return ((total_value - total_cost) / total_cost) * 100

    def calculate_daily_return(self, portfolio: Portfolio, prices: Dict[str, float], prev_prices: Dict[str, float]) -> float:
        current_value = 0.0
        prev_value = 0.0
        for item in portfolio.items:
            current_value += item.quantity * prices.get(item.ticker, 0)
            prev_value += item.quantity * prev_prices.get(item.ticker, prices.get(item.ticker, 0))
        if prev_value == 0:
            return 0.0
        return ((current_value - prev_value) / prev_value) * 100

    def calculate_cagr(self, portfolio: Portfolio, price_history: pd.DataFrame, years: float) -> float:
        if price_history.empty or years <= 0:
            return 0.0
        try:
            tickers = [item.ticker for item in portfolio.items]
            available = [t for t in tickers if t in price_history.columns]
            if not available:
                return 0.0

            weights = {}
            total_cost = sum(item.quantity * item.cost_basis for item in portfolio.items)
            for item in portfolio.items:
                weights[item.ticker] = (item.quantity * item.cost_basis) / total_cost if total_cost > 0 else 0

            start_prices = price_history.iloc[0]
            end_prices = price_history.iloc[-1]

            start_val = sum(weights.get(t, 0) * start_prices[t] for t in available if t in start_prices)
            end_val = sum(weights.get(t, 0) * end_prices[t] for t in available if t in end_prices)

            if start_val <= 0:
                return 0.0
            return ((end_val / start_val) ** (1 / years) - 1) * 100
        except Exception:
            return 0.0

    def get_allocation(self, portfolio: Portfolio, prices: Dict[str, float]) -> Dict[str, float]:
        values = self.calculate_current_value(portfolio, prices)
        total = sum(values.values())
        if total == 0:
            return {}
        return {ticker: (val / total) * 100 for ticker, val in values.items()}
