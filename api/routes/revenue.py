from fastapi import APIRouter
from api.models.schemas import RevenueInput, RevenueOutput
from api.services.revenue import calculate_revenue

router = APIRouter()

@router.post("/calculate", response_model=RevenueOutput)
async def calculate_revenue_endpoint(input_data: RevenueInput) -> RevenueOutput:
    """Calculate revenue based on input parameters."""
    return calculate_revenue(input_data) 