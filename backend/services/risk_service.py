import pandas as pd
import numpy as np
from typing import Dict, Optional
from backend.models.portfolio import Portfolio


class RiskService:
    def volatility(self, returns: pd.Series) -> float:
        try:
            if returns.empty or len(returns) < 2:
                return 0.0
            return float(returns.std() * np.sqrt(252) * 100)
        except Exception:
            return 0.0

    def sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.05) -> float:
        try:
            if returns.empty or len(returns) < 2:
                return 0.0
            daily_rf = risk_free_rate / 252
            excess = returns - daily_rf
            if excess.std() == 0:
                return 0.0
            return float((excess.mean() / excess.std()) * np.sqrt(252))
        except Exception:
            return 0.0

    def max_drawdown(self, prices: pd.Series) -> float:
        try:
            if prices.empty or len(prices) < 2:
                return 0.0
            cumulative = (1 + prices.pct_change().dropna()).cumprod()
            rolling_max = cumulative.cummax()
            drawdown = (cumulative - rolling_max) / rolling_max
            return float(drawdown.min() * 100)
        except Exception:
            return 0.0

    def correlation_matrix(self, price_data: pd.DataFrame) -> pd.DataFrame:
        try:
            if price_data.empty:
                return pd.DataFrame()
            returns = price_data.pct_change().dropna()
            return returns.corr()
        except Exception:
            return pd.DataFrame()

    def calculate_portfolio_risk(self, portfolio: Portfolio, price_data: pd.DataFrame) -> dict:
        try:
            if price_data.empty:
                return {
                    "volatility": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "correlation_matrix": {},
                }

            tickers = [item.ticker for item in portfolio.items]
            available = [t for t in tickers if t in price_data.columns]

            if not available:
                return {
                    "volatility": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "correlation_matrix": {},
                }

            subset = price_data[available].dropna()
            total_cost = sum(item.quantity * item.cost_basis for item in portfolio.items)
            weights = np.array([
                (item.quantity * item.cost_basis) / total_cost if total_cost > 0 else 1 / len(available)
                for item in portfolio.items if item.ticker in available
            ])
            weights = weights / weights.sum()

            returns = subset.pct_change().dropna()
            portfolio_returns = returns.dot(weights)

            vol = self.volatility(portfolio_returns)
            sharpe = self.sharpe_ratio(portfolio_returns)

            portfolio_prices = (1 + portfolio_returns).cumprod()
            mdd = self.max_drawdown(portfolio_prices)

            corr = self.correlation_matrix(subset)

            return {
                "volatility": vol,
                "sharpe_ratio": sharpe,
                "max_drawdown": mdd,
                "correlation_matrix": corr.to_dict() if not corr.empty else {},
            }
        except Exception:
            return {
                "volatility": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "correlation_matrix": {},
            }
