"""
Configuration module for Commodity Portfolio Monte Carlo Simulation

All parameters can be adjusted according to analysis requirements.
For production use, consider moving sensitive parameters to environment variables.
"""

from typing import List
from datetime import datetime
import os

# ======================
# CORE CONFIGURATION
# ======================

# Commodity tickers (Yahoo Finance format)
COMMODITIES: List[str] = [
    'GC=F',  # Gold
    'SI=F',  # Silver
    'CL=F',  # Crude Oil (WTI)
    'NG=F',  # Natural Gas
    'ZC=F'   # Corn
]

# Date range for historical data (YYYY-MM-DD format)
START_DATE: str = '2015-01-01'
END_DATE: str = '2023-01-01'

# Risk-free rate (annualized)
RISK_FREE_RATE: float = 0.02  # 2%

# Simulation parameters
MONTE_CARLO_SIMS: int = 1000  # Number of simulations
TIME_HORIZON: int = 252        # Trading days (1 year)

# ======================
# ADVANCED SETTINGS
# ======================

# Data fetching parameters
YFINANCE_RETRIES: int = 3               # Number of download attempts
YFINANCE_TIMEOUT: int = 10              # Seconds before timeout
YFINANCE_INTERVAL: str = '1d'            # Data interval ('1d', '1wk', '1mo')

# Portfolio optimization
EFFICIENT_FRONTIER_POINTS: int = 10000  # Random portfolios to generate
MIN_WEIGHT: float = 0.05                # Minimum asset weight in optimization

# Output configuration
OUTPUT_DIR: str = 'outputs'              # Directory for results
EXCEL_TEMPLATE: str = None               # Path to Excel template (optional)
PLOT_STYLE: str = 'seaborn'              # Matplotlib style ('seaborn', 'ggplot', etc.)

# ======================
# VALIDATION & DERIVED PARAMS
# ======================

def _validate_config():
    """Validate configuration parameters"""
    assert len(COMMODITIES) > 1, "At least 2 commodities required"
    assert 0 <= RISK_FREE_RATE <= 0.1, "Risk-free rate should be between 0% and 10%"
    assert MONTE_CARLO_SIMS >= 100, "Minimum 100 simulations required"
    assert TIME_HORIZON >= 30, "Minimum 30 day horizon required"
    
    try:
        datetime.strptime(START_DATE, '%Y-%m-%d')
        datetime.strptime(END_DATE, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

# Create output directory if needed
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Validate configuration on import
_validate_config()

# ======================
# DOCUMENTATION
# ======================

__doc__ = """
Configuration Options:

1. COMMODITIES: List of commodity tickers from Yahoo Finance
   - Example: ['GC=F', 'CL=F'] for Gold and Crude Oil

2. DATE RANGE:
   - START_DATE: Beginning of historical data period
   - END_DATE: End of historical data period

3. FINANCIAL PARAMETERS:
   - RISK_FREE_RATE: Used for Sharpe ratio calculations

4. SIMULATION PARAMETERS:
   - MONTE_CARLO_SIMS: Number of simulation paths
   - TIME_HORIZON: Projection period in trading days

5. ADVANCED SETTINGS:
   - Data fetching, optimization constraints, and output preferences
"""

def print_config_summary():
    """Display key configuration parameters"""
    print("\nConfiguration Summary:")
    print(f"Commodities: {', '.join(COMMODITIES)}")
    print(f"Date Range: {START_DATE} to {END_DATE}")
    print(f"Risk-free Rate: {RISK_FREE_RATE:.2%}")
    print(f"Monte Carlo Simulations: {MONTE_CARLO_SIMS:,}")
    print(f"Time Horizon: {TIME_HORIZON} days (~{TIME_HORIZON//21} months)")
    print(f"Output Directory: {os.path.abspath(OUTPUT_DIR)}")