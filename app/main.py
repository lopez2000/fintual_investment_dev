from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import logging
from typing import Optional
from app.optimizer import PortfolioOptimizer
from app.schemas import OptimizePortfolioRequest, OptimizePortfolioResponse, ErrorResponse
from datetime import datetime
from io import StringIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Portfolio Optimization API",
    description="API for optimizing investment portfolios using Markowitz mean-variance optimization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/optimize-portfolio")
async def optimize_portfolio(
    file: UploadFile = File(..., description="CSV file containing historical returns data"),
    risk_level: float = Form(..., description="Target portfolio volatility"),
    max_weight: float = Form(..., description="Maximum weight per asset"),
    min_weight: Optional[float] = Form(None, description="Minimum weight per asset"),
    target_return: Optional[float] = Form(None, description="Target portfolio return")
):
    """
    Optimize a portfolio using Markowitz mean-variance optimization.
    Returns only the optimal_portfolio dictionary as required.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        df.set_index(df.columns[0], inplace=True)
        df = df.dropna()
        if df.empty:
            raise HTTPException(status_code=400, detail="The uploaded file contains no valid data after removing missing values")
        optimizer = PortfolioOptimizer(df)
        result = optimizer.optimize(
            risk_level=risk_level,
            max_weight=max_weight,
            min_weight=min_weight,
            target_return=target_return
        )
        return {"optimal_portfolio": result["optimal_portfolio"]}
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during portfolio optimization")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Status of the API
    """
    return {"status": "healthy", "timestamp": datetime.now()} 