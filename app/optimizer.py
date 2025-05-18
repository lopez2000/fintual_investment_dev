import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """
    Implements Markowitz mean-variance portfolio optimization to maximize the Sharpe ratio.
    """
    def __init__(self, returns: pd.DataFrame):
        """
        Initialize with a DataFrame of asset returns.
        :param returns: DataFrame with columns as assets and rows as returns.
        """
        self.returns = returns
        self.mean_returns = returns.mean()
        self.cov_matrix = returns.cov()

    def optimize(self, risk_level: float, max_weight: float) -> Dict[str, float]:
        """
        Optimize the portfolio to maximize the Sharpe ratio, subject to risk and weight constraints.
        :param risk_level: Target portfolio volatility (risk).
        :param max_weight: Maximum weight per asset.
        :return: Dictionary of asset weights.
        """
        num_assets = len(self.mean_returns)
        bounds = tuple((0, max_weight) for _ in range(num_assets))
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        x0 = np.array([1.0 / num_assets] * num_assets)

        def neg_sharpe(weights):
            port_return = np.dot(weights, self.mean_returns)
            port_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            if port_vol == 0:
                return 0
            return -port_return / port_vol

        result = minimize(neg_sharpe, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        if not result.success:
            logger.error(f"Optimization failed: {result.message}")
            raise ValueError(f"Optimization failed: {result.message}")
        weights = result.x
        return dict(zip(self.mean_returns.index, weights))

    @staticmethod
    def from_csv(file_path: str) -> 'PortfolioOptimizer':
        """
        Create a PortfolioOptimizer from a CSV file.
        :param file_path: Path to the CSV file.
        :return: PortfolioOptimizer instance.
        """
        returns = pd.read_csv(file_path, index_col=0)
        return PortfolioOptimizer(returns)
