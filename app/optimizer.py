import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, Tuple, Optional
import logging
from app.utils import max_weight_fallback, validate_returns_data, calculate_portfolio_metrics
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """
    A class implementing Markowitz mean-variance portfolio optimization.
    
    This optimizer uses modern portfolio theory to find the optimal asset weights
    that maximize the Sharpe ratio while respecting risk and weight constraints.
    """
    
    def __init__(self, returns: pd.DataFrame, risk_free_rate: float = 0.02):
        """
        Initialize the optimizer with historical returns data.
        
        Args:
            returns: DataFrame of historical returns with assets as columns
            risk_free_rate: Annual risk-free rate (default: 2%)
        """
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        self.mean_returns = returns.mean()
        self.cov_matrix = returns.cov()
        self.n_assets = len(returns.columns)
        
    def _portfolio_stats(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate portfolio statistics.
        
        Args:
            weights: Array of asset weights
            
        Returns:
            Tuple of (expected_return, volatility, sharpe_ratio)
        """
        portfolio_return = np.sum(self.mean_returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
        return portfolio_return, portfolio_vol, sharpe_ratio
    
    def _objective(self, weights: np.ndarray, target_vol: Optional[float] = None) -> float:
        """
        Objective function for optimization.
        
        Args:
            weights: Array of asset weights
            target_vol: Target portfolio volatility (optional)
            
        Returns:
            Negative Sharpe ratio (to minimize)
        """
        portfolio_return, portfolio_vol, sharpe_ratio = self._portfolio_stats(weights)
        
        if target_vol is not None:
            # Penalize deviation from target volatility
            vol_penalty = 1000 * (portfolio_vol - target_vol) ** 2
            return -sharpe_ratio + vol_penalty
        
        return -sharpe_ratio
    
    def optimize(
        self,
        risk_level: float,
        max_weight: float,
        min_weight: Optional[float] = None,
        target_return: Optional[float] = None
    ) -> Dict:
        """
        Optimize portfolio weights using mean-variance optimization.
        
        Args:
            risk_level: Target portfolio volatility
            max_weight: Maximum weight per asset
            min_weight: Minimum weight per asset (optional)
            target_return: Target portfolio return (optional)
            
        Returns:
            Dictionary containing optimal weights and portfolio statistics
        """
        # Input validation
        if risk_level <= 0 or risk_level > 1:
            raise ValueError("risk_level must be between 0 and 1")
        if max_weight <= 0 or max_weight > 1:
            raise ValueError("max_weight must be between 0 and 1")
        if min_weight is not None and (min_weight < 0 or min_weight > max_weight):
            raise ValueError("min_weight must be between 0 and max_weight")
            
        # Check if optimization is possible
        if max_weight * self.n_assets < 1:
            raise ValueError(
                f"Impossible to construct portfolio: max_weight * n_assets ({max_weight * self.n_assets}) < 1"
            )
            
        # Handle single asset case
        if self.n_assets == 1:
            return {
                "optimal_portfolio": {self.returns.columns[0]: 1.0},
                "expected_return": float(self.mean_returns.iloc[0]),
                "expected_volatility": float(np.sqrt(self.cov_matrix.iloc[0, 0])),
                "sharpe_ratio": float((self.mean_returns.iloc[0] - self.risk_free_rate) / 
                                    np.sqrt(self.cov_matrix.iloc[0, 0])),
                "optimization_timestamp": datetime.now(timezone.utc)
            }
            
        # Initial guess (equal weights)
        initial_weights = np.array([1/self.n_assets] * self.n_assets)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # weights sum to 1
        ]
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.sum(self.mean_returns * x) - target_return
            })
            
        # Bounds
        bounds = [(min_weight or 0, max_weight) for _ in range(self.n_assets)]
        
        try:
            # Optimize
            result = minimize(
                self._objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                args=(risk_level,)
            )
            
            if not result.success:
                logger.warning(f"Optimization warning: {result.message}")
                # Fallback to equal weights if optimization fails
                weights = initial_weights
            else:
                weights = result.x
                
            # Calculate portfolio statistics
            expected_return, expected_vol, sharpe_ratio = self._portfolio_stats(weights)
            
            return {
                "optimal_portfolio": dict(zip(self.returns.columns, weights)),
                "expected_return": float(expected_return),
                "expected_volatility": float(expected_vol),
                "sharpe_ratio": float(sharpe_ratio),
                "optimization_timestamp": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            raise ValueError(f"Portfolio optimization failed: {str(e)}")

    @staticmethod
    def from_csv(file_path: str) -> 'PortfolioOptimizer':
        """
        Create a PortfolioOptimizer from a CSV file.
        :param file_path: Path to the CSV file.
        :return: PortfolioOptimizer instance.
        """
        returns = pd.read_csv(file_path, index_col=0)
        return PortfolioOptimizer(returns)
