import pytest
import pandas as pd
import numpy as np
from app.optimizer import PortfolioOptimizer

def test_optimize_portfolio_basic():
    """Test basic portfolio optimization with simple data."""
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
    result = optimizer.optimize(risk_level, max_weight)
    
    # Check that weights sum to 1
    assert np.isclose(sum(result['optimal_portfolio'].values()), 1.0)
    # Check that all weights are between 0 and max_weight
    assert all(0 <= w <= max_weight for w in result['optimal_portfolio'].values())
    # Check that we have all expected fields
    assert 'expected_return' in result
    assert 'expected_volatility' in result
    assert 'sharpe_ratio' in result
    assert 'optimization_timestamp' in result

def test_optimize_portfolio_edge_cases():
    """Test portfolio optimization with edge cases."""
    # Create returns with very different characteristics
    data = {
        'High_Return': [0.05, 0.06, 0.04, 0.05],  # High return, high volatility
        'Low_Return': [0.01, 0.01, 0.01, 0.01],   # Low return, low volatility
        'Zero_Return': [0.0, 0.0, 0.0, 0.0]       # Zero return
    }
    returns = pd.DataFrame(data)
    optimizer = PortfolioOptimizer(returns)

    # Test with very low max_weight (should raise ValueError)
    with pytest.raises(ValueError):
        optimizer.optimize(risk_level=0.1, max_weight=0.3)

    # Test with very high max_weight
    result = optimizer.optimize(risk_level=0.1, max_weight=0.9)
    assert all(w <= 0.9 for w in result['optimal_portfolio'].values())
    assert np.isclose(sum(result['optimal_portfolio'].values()), 1.0)

def test_optimize_portfolio_invalid_inputs():
    """Test portfolio optimization with invalid inputs."""
    data = {
        'A': [0.01, 0.02, 0.015],
        'B': [0.02, 0.01, 0.005]
    }
    returns = pd.DataFrame(data)
    optimizer = PortfolioOptimizer(returns)

    # Test invalid risk_level
    with pytest.raises(ValueError):
        optimizer.optimize(risk_level=-0.1, max_weight=0.5)
    with pytest.raises(ValueError):
        optimizer.optimize(risk_level=1.5, max_weight=0.5)

    # Test invalid max_weight
    with pytest.raises(ValueError):
        optimizer.optimize(risk_level=0.1, max_weight=-0.1)
    with pytest.raises(ValueError):
        optimizer.optimize(risk_level=0.1, max_weight=1.5)

    # Test invalid min_weight
    with pytest.raises(ValueError):
        optimizer.optimize(risk_level=0.1, max_weight=0.5, min_weight=0.6)

def test_optimize_portfolio_single_asset():
    """Test portfolio optimization with a single asset."""
    data = {'A': [0.01, 0.02, 0.015, -0.005]}
    returns = pd.DataFrame(data)
    optimizer = PortfolioOptimizer(returns)
    result = optimizer.optimize(risk_level=0.1, max_weight=1.0)

    # With single asset, weight should be 1.0
    assert len(result['optimal_portfolio']) == 1
    assert result['optimal_portfolio']['A'] == 1.0
    assert 'expected_return' in result
    assert 'expected_volatility' in result
    assert 'sharpe_ratio' in result

def test_optimize_portfolio_negative_returns():
    """Test portfolio optimization with negative returns."""
    data = {
        'A': [-0.01, -0.02, -0.015, -0.005],
        'B': [-0.02, -0.01, -0.005, -0.01]
    }
    returns = pd.DataFrame(data)
    optimizer = PortfolioOptimizer(returns)
    result = optimizer.optimize(risk_level=0.1, max_weight=0.7)

    # Check basic constraints
    assert np.isclose(sum(result['optimal_portfolio'].values()), 1.0)
    assert all(0 <= w <= 0.7 for w in result['optimal_portfolio'].values())
    assert result['expected_volatility'] > 0
    assert 'sharpe_ratio' in result
