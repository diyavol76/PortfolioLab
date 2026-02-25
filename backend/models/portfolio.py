from pydantic import BaseModel, Field
from typing import List, Optional


class PortfolioItem(BaseModel):
    ticker: str
    quantity: float
    cost_basis: float  # cost per share


class Portfolio(BaseModel):
    name: str = "My Portfolio"
    items: List[PortfolioItem] = []


class AddStockRequest(BaseModel):
    ticker: str
    quantity: float = Field(gt=0)
    cost_basis: float = Field(gt=0)


class PortfolioResponse(BaseModel):
    items: List[PortfolioItem]
    total_value: float
    total_cost: float
    total_return_pct: float
    daily_return_pct: float
