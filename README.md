# Market Mapper Calculator API

A FastAPI-based calculation service for the Market Mapper application, handling complex financial calculations and data processing.

## Features
- Revenue calculations with inflation adjustments
- Historical data processing
- Growth rate analysis
- RESTful API endpoints

## Tech Stack
- Python 3.13
- FastAPI
- NumPy
- Pandas
- Vercel Serverless Functions

## Local Development
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
uvicorn api.calculate_revenue:app --reload
```

## API Endpoints
- `GET /`: Health check endpoint
- `POST /calculate`: Calculate revenue projections

## Deployment
This service is deployed on Vercel as serverless functions. 