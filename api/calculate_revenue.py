from fastapi import FastAPI
from api.routes.revenue import router as revenue_router

app = FastAPI(
    title="Market Mapper Calculator",
    description="API for calculating market size and revenue projections",
    version="1.0.0"
)

app.include_router(revenue_router, prefix="/api", tags=["revenue"])

@app.get("/")
async def root():
    return {"message": "Market Mapper Calculator API is running"} 