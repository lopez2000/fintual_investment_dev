import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

def max_weight_fallback(asset_names: List[str], max_weight: float) -> Dict[str, float]:
    """
    Create a fallback portfolio when optimization fails, respecting max_weight constraint.
    
    Args:
        asset_names: List of asset names
        max_weight: Maximum allowed weight per asset
        
    Returns:
        Dictionary of asset weights
    """
    n = len(asset_names)
    weights = [0.0] * n
    max_assets = int(1 // max_weight)
    remainder = 1.0 - (max_assets * max_weight)
    for i in range(max_assets):
        weights[i] = max_weight
    if max_assets < n:
        weights[max_assets] = remainder
    return dict(zip(asset_names, weights))

def validate_returns_data(returns: pd.DataFrame) -> None:
    """
    Validate returns data for portfolio optimization.
    
    Args:
        returns: DataFrame with asset returns
        
    Raises:
        ValueError: If data is invalid
    """
    if returns.empty:
        raise ValueError("Returns DataFrame is empty")
    if returns.isnull().any().any():
        raise ValueError("Returns DataFrame contains missing values")

def calculate_portfolio_metrics(weights: Dict[str, float], 
                              mean_returns: pd.Series, 
                              cov_matrix: pd.DataFrame) -> Tuple[float, float, float]:
    """
    Calculate portfolio return, volatility, and Sharpe ratio.
    
    Args:
        weights: Dictionary of asset weights
        mean_returns: Series of mean returns
        cov_matrix: Covariance matrix of returns
        
    Returns:
        Tuple of (portfolio_return, portfolio_volatility, sharpe_ratio)
    """
    w = np.array(list(weights.values()))
    port_return = np.dot(w, mean_returns)
    port_vol = np.sqrt(w.T @ cov_matrix @ w)
    sharpe_ratio = port_return / port_vol if port_vol > 0 else 0
    return port_return, port_vol, sharpe_ratio
