import pytest
import pandas as pd
import numpy as np
from app.optimizer import PortfolioOptimizer

def test_optimize_portfolio_basic():
    # Create a small returns DataFrame
    data = {
        'A': [0.01, 0.02, 0.015, -0.005],
        'B': [0.02, 0.01, 0.005, 0.0],
        'C': [-0.01, 0.0, 0.01, 0.02]
    }
    returns = pd.DataFrame(data)
    optimizer = PortfolioOptimizer(returns)
    risk_level = 0.1
    max_weight = 0.7
    weights = optimizer.optimize(risk_level, max_weight)
    # Check that weights sum to 1
    assert np.isclose(sum(weights.values()), 1.0)
    # Check that no weight exceeds max_weight and all are >= 0
    for w in weights.values():
        assert 0 <= w <= max_weight
