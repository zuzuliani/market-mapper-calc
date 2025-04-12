import numpy as np
from api.models.schemas import RevenueInput, RevenueOutput

def calculate_revenue(input_data: RevenueInput) -> RevenueOutput:
    """Calculate revenue based on market size, share, and growth rate."""
    
    # Calculate base revenue
    base_revenue = input_data.market_size * input_data.market_share * input_data.price_point
    
    # Calculate yearly revenues with growth
    yearly_revenues = []
    for year in range(input_data.time_horizon):
        year_revenue = base_revenue * (1 + input_data.growth_rate) ** year
        yearly_revenues.append(year_revenue)
    
    return RevenueOutput(
        revenue=sum(yearly_revenues),
        yearly_revenue=yearly_revenues,
        market_size=input_data.market_size,
        market_share=input_data.market_share
    ) 