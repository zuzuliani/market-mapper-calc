from pydantic import BaseModel
from typing import List, Optional

class RevenueInput(BaseModel):
    market_size: float
    market_share: float
    price_point: float
    growth_rate: Optional[float] = 0.0
    time_horizon: Optional[int] = 1

class RevenueOutput(BaseModel):
    revenue: float
    yearly_revenue: List[float]
    market_size: float
    market_share: float 