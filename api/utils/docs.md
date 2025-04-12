# Market Mapper Calculator API Documentation

## Project Overview
The Market Mapper Calculator is a FastAPI-based service that provides revenue calculations based on market size, market share, and growth projections.

## Architecture

### Directory Structure
```
market-mapper-calc/
├── api/
│   ├── __init__.py
│   ├── calculate_revenue.py    # Main FastAPI application
│   ├── routes/
│   │   ├── __init__.py
│   │   └── revenue.py         # API route handlers
│   ├── services/
│   │   ├── __init__.py
│   │   └── revenue.py         # Business logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Data models
│   └── utils/
│       ├── __init__.py
│       └── docs.md            # Documentation
```

### Components
1. **Main Application** (`calculate_revenue.py`)
   - FastAPI application setup
   - Router registration
   - Base endpoint configuration

2. **Routes** (`routes/revenue.py`)
   - API endpoint definitions
   - Request/response handling
   - Route documentation

3. **Services** (`services/revenue.py`)
   - Core business logic
   - Revenue calculations
   - Data processing

4. **Models** (`models/schemas.py`)
   - Pydantic models for request/response validation
   - Data structure definitions

## API Endpoints

### 1. Health Check
- **URL**: `/`
- **Method**: GET
- **Response**: `{"message": "Market Mapper Calculator API is running"}`

### 2. Calculate Revenue
- **URL**: `/api/calculate`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "market_size": float,
    "market_share": float,
    "price_point": float,
    "growth_rate": float,
    "time_horizon": int
  }
  ```
- **Response**:
  ```json
  {
    "revenue": float,
    "yearly_revenue": [float],
    "market_size": float,
    "market_share": float
  }
  ```

## Deployment

### Vercel Configuration
The project is deployed on Vercel with the following configuration (`vercel.json`):
```json
{
  "version": 2,
  "builds": [
    { "src": "api/calculate_revenue.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "api/calculate_revenue.py" }
  ]
}
```

### Dependencies
Required Python packages (from `requirements.txt`):
- fastapi==0.104.1
- uvicorn==0.24.0
- numpy==1.26.2
- pydantic==2.5.2

## Development Notes

### Package Structure
- Each directory contains an `__init__.py` file to make it a proper Python package
- Relative imports are replaced with absolute imports for Vercel compatibility
- Example: `from api.models.schemas import RevenueInput` instead of `from ..models.schemas import RevenueInput`

### Calculation Logic
The revenue calculation follows these steps:
1. Calculate base revenue: `market_size * market_share * price_point`
2. Apply growth rate for each year: `base_revenue * (1 + growth_rate)^year`
3. Sum all yearly revenues for total revenue

Example calculation:
- Input:
  ```json
  {
    "market_size": 1000000,
    "market_share": 0.1,
    "price_point": 100,
    "growth_rate": 0.05,
    "time_horizon": 3
  }
  ```
- Yearly breakdown:
  - Year 1: $10,000,000
  - Year 2: $10,500,000 (5% growth)
  - Year 3: $11,025,000 (5% growth)
  - Total: $31,525,000

## Testing
You can test the API using:
1. **PowerShell**:
   ```powershell
   Invoke-RestMethod -Uri "https://market-mapper-calc.vercel.app/api/calculate" -Method Post -Body '{"market_size":1000000,"market_share":0.1,"price_point":100,"growth_rate":0.05,"time_horizon":3}' -ContentType "application/json"
   ```

2. **Python** (`test_api.py`):
   ```python
   import requests
   response = requests.post(url, json=data)
   ```

## Learnings and Best Practices
1. **Modular Structure**: Separating concerns into routes, services, and models improves maintainability
2. **Vercel Deployment**: 
   - Use absolute imports
   - Configure `vercel.json` properly
   - Include all necessary `__init__.py` files
3. **Type Hints**: Using Pydantic models ensures proper request/response validation
4. **Documentation**: Keep API documentation updated with examples and clear descriptions 