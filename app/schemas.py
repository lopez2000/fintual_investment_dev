from pydantic import BaseModel, Field
from typing import Dict

class OptimizePortfolioResponse(BaseModel):
    optimal_portfolio: Dict[str, float] = Field(..., description="Optimal asset weights")

# For future extensibility, a request model could be defined as:
# class OptimizePortfolioRequest(BaseModel):
#     risk_level: float
#     max_weight: float
