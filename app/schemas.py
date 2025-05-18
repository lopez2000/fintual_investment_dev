from pydantic import BaseModel, Field, validator, confloat
from typing import Dict, Optional
from fastapi import UploadFile
from datetime import datetime, timezone

class OptimizePortfolioRequest(BaseModel):
    """
    Request model for portfolio optimization.
    
    This model handles the input parameters for the Markowitz mean-variance optimization,
    ensuring all constraints are met before processing.
    """
    risk_level: confloat(gt=0, le=1) = Field(
        ...,
        description="Target portfolio volatility (risk level) as a decimal between 0 and 1",
        example=0.15
    )
    max_weight: confloat(gt=0, le=1) = Field(
        ...,
        description="Maximum weight allowed per asset as a decimal between 0 and 1",
        example=0.3
    )
    min_weight: Optional[confloat(ge=0, le=1)] = Field(
        None,
        description="Minimum weight allowed per asset (optional)",
        example=0.05
    )
    target_return: Optional[float] = Field(
        None,
        description="Target portfolio return (optional). If not provided, optimization will maximize Sharpe ratio",
        example=0.08
    )

    @validator('max_weight')
    def validate_max_weight(cls, v):
        if v <= 0 or v > 1:
            raise ValueError('max_weight must be between 0 and 1')
        return v

    @validator('risk_level')
    def validate_risk_level(cls, v):
        if v <= 0 or v > 1:
            raise ValueError('risk_level must be between 0 and 1')
        return v

    @validator('min_weight')
    def validate_min_weight(cls, v, values):
        if v is not None:
            if 'max_weight' in values and v > values['max_weight']:
                raise ValueError('min_weight cannot be greater than max_weight')
        return v

class OptimizePortfolioResponse(BaseModel):
    """
    Response model for portfolio optimization.
    
    Contains the optimal portfolio weights and key performance metrics
    calculated using the Markowitz mean-variance optimization.
    """
    optimal_portfolio: Dict[str, float] = Field(
        ...,
        description="Dictionary of asset weights in the optimal portfolio",
        example={
            "SPY US Equity": 0.3,
            "QQQ US Equity": 0.4,
            "IWM US Equity": 0.3
        }
    )
    expected_return: float = Field(
        ...,
        description="Expected annual return of the optimal portfolio",
        example=0.085
    )
    expected_volatility: float = Field(
        ...,
        description="Expected annual volatility of the optimal portfolio",
        example=0.15
    )
    sharpe_ratio: float = Field(
        ...,
        description="Sharpe ratio of the optimal portfolio (assuming risk-free rate of 0.02)",
        example=1.5
    )
    optimization_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of when the optimization was performed"
    )

    @validator('optimal_portfolio')
    def validate_weights(cls, v):
        # Check if weights sum to 1
        if not abs(sum(v.values()) - 1.0) < 1e-6:
            raise ValueError('Portfolio weights must sum to 1')
        # Check if all weights are between 0 and 1
        if not all(0 <= w <= 1 for w in v.values()):
            raise ValueError('All weights must be between 0 and 1')
        return v

class ErrorResponse(BaseModel):
    """
    Standard error response model for consistent error handling across the API.
    """
    detail: str = Field(
        ...,
        description="Error message describing what went wrong",
        example="The uploaded file contains missing values"
    )
    error_code: str = Field(
        ...,
        description="Machine-readable error code for programmatic handling",
        example="INVALID_INPUT"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the error occurred"
    )

# For future extensibility, a request model could be defined as:
# class OptimizePortfolioRequest(BaseModel):
#     risk_level: float
#     max_weight: float
