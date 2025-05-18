from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.optimizer import PortfolioOptimizer
from app.schemas import OptimizePortfolioResponse
import pandas as pd
import logging
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/optimize-portfolio", response_model=OptimizePortfolioResponse)
def optimize_portfolio(
    file: UploadFile = File(...),
    risk_level: float = Form(...),
    max_weight: float = Form(...)
) -> OptimizePortfolioResponse:
    """
    Optimize a portfolio using Markowitz mean-variance optimization to maximize the Sharpe ratio.
    """
    try:
        # Save uploaded file to a temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        # Read returns
        returns = pd.read_csv(tmp_path, index_col=0)
        optimizer = PortfolioOptimizer(returns)
        optimal_weights = optimizer.optimize(risk_level, max_weight)
        return OptimizePortfolioResponse(optimal_portfolio=optimal_weights)
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        raise HTTPException(status_code=400, detail=str(e)) 