# Portfolio Optimization Service

This service implements Modern Portfolio Theory (MPT) for optimizing investment portfolios using Markowitz mean-variance optimization to maximize the Sharpe ratio.

## Project Structure

```
fintual_investment_dev/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI entrypoint
│   ├── optimizer.py      # Portfolio optimization logic
│   ├── schemas.py        # Pydantic models for request/response
│   └── utils.py          # (Optional) Helper functions
├── tests/
│   └── test_optimizer.py # Unit tests
├── requirements.txt
├── README.md
└── returns.csv           # Example data
```

## Optimization Method

The service implements a sophisticated portfolio optimization strategy based on Modern Portfolio Theory (MPT) with the following key features:

### 1. Sharpe Ratio Maximization
- The optimizer maximizes the Sharpe ratio, which measures risk-adjusted returns
- This approach balances both return and risk, rather than just maximizing returns
- The Sharpe ratio is calculated as: (Portfolio Return - Risk-Free Rate) / Portfolio Volatility

### 2. Implementation Details
- Uses the Sequential Least Squares Programming (SLSQP) algorithm for optimization
- Implements the following constraints:
  - Full investment (weights sum to 1)
  - No short selling (weights ≥ 0)
  - Maximum weight per asset (user-defined)
  - Target risk level (user-defined volatility)

### 3. Why This Approach?
1. **Risk-Adjusted Returns**: By maximizing the Sharpe ratio, we focus on efficient portfolios that provide the best return per unit of risk
2. **Practical Constraints**: The implementation includes real-world constraints like maximum position sizes and no short selling
3. **Flexibility**: Users can adjust risk levels and maximum weights to match their investment preferences
4. **Robustness**: The SLSQP algorithm is well-suited for constrained optimization problems with non-linear objectives

### 4. Mathematical Formulation
The optimization problem is formulated as:
```
maximize: (w'μ - rf) / √(w'Σw)
subject to:
    w'1 = 1
    0 ≤ w ≤ max_weight
    √(w'Σw) ≤ risk_level
```
where:
- w: vector of portfolio weights
- μ: vector of expected returns
- Σ: covariance matrix
- rf: risk-free rate
- max_weight: maximum allowed weight per asset
- risk_level: target portfolio volatility

## API Usage

- **Endpoint:** `/optimize-portfolio` (POST)
- **Input:**
  - `file`: CSV file with daily returns (first column: date, other columns: asset returns)
  - `risk_level`: Target portfolio volatility (float)
  - `max_weight`: Maximum weight per asset (float)
- **Response:**
  - JSON with the optimal portfolio weights

### Example Request (using `curl`):

```
curl -X POST "http://127.0.0.1:8000/optimize-portfolio" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@returns.csv;type=text/csv" \
  -F "risk_level=0.15" \
  -F "max_weight=0.4"
```

### Example Response

```
{
  "optimal_portfolio": {
    "SPY US Equity": 0.2,
    "QQQ US Equity": 0.4,
    "IWM US Equity": 0.4
  }
}
```

## Running the Service

1. **Install dependencies:**
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Start the server:**
   ```
   uvicorn app.main:app --reload
   ```

## Running Tests

Unit tests are provided using `pytest`:

```
pytest
```

## Best Practices
- Modular code: Business logic is separated from API logic
- Type annotations and docstrings throughout
- Robust error handling and logging
- Automated tests for reliability
- Professional project structure and `.gitignore`

## Dependencies
- fastapi: Modern web framework for building APIs
- pandas: Data manipulation and analysis
- numpy: Numerical computing
- scipy: Scientific computing and optimization
- uvicorn: ASGI server
- python-multipart: File upload handling
- pytest: Testing framework

---

**For more about the role and expectations, see the [Fintual Investment Solutions Developer job description](https://jobs.lever.co/fintual/5962de0a-328f-4889-a9ff-cf2a171f2e18).**