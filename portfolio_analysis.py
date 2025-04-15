import numpy as np
import pandas as pd
from yfinance import download
from scipy.stats import norm
from typing import List, Tuple
from config import RISK_FREE_RATE  # Using centralized configuration

def fetch_commodity_data(commodities: List[str], 
                        start_date: str, 
                        end_date: str,
                        max_retries: int = 3) -> pd.DataFrame:
    """
    Fetch historical commodity prices with error handling
    
    Args:
        commodities: List of commodity tickers
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        max_retries: Maximum number of download attempts
        
    Returns:
        DataFrame with adjusted closing prices
        
    Raises:
        ConnectionError: If data cannot be fetched after retries
    """
    for attempt in range(max_retries):
        try:
            data = download(commodities, start=start_date, end=end_date)['Adj Close']
            if data.empty:
                raise ValueError("No data returned from yfinance")
            return data.dropna()
        except Exception as e:
            if attempt == max_retries - 1:
                raise ConnectionError(f"Failed to fetch data after {max_retries} attempts: {str(e)}")
            continue

def calculate_daily_returns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily log returns with validation
    
    Args:
        data: DataFrame with price data
        
    Returns:
        DataFrame with daily log returns
        
    Raises:
        ValueError: If input data contains non-positive values
    """
    if (data <= 0).any().any():
        raise ValueError("Price data must be positive for log returns")
    
    returns = np.log(data / data.shift(1))
    return returns.dropna()

def calculate_portfolio_stats(returns: pd.DataFrame, 
                            weights: np.ndarray,
                            trading_days: int = 252) -> Tuple[float, float, float]:
    """
    Calculate portfolio statistics with validation
    
    Args:
        returns: DataFrame of asset returns
        weights: Array of portfolio weights
        trading_days: Number of trading days in a year
        
    Returns:
        Tuple of (annualized_return, annualized_volatility, sharpe_ratio)
        
    Raises:
        ValueError: If weights don't sum to 1 or have wrong dimensions
    """
    # Validate weights
    if not np.isclose(weights.sum(), 1, rtol=0.01):
        raise ValueError("Weights must sum to 1")
    if len(weights) != returns.shape[1]:
        raise ValueError("Number of weights must match number of assets")
    
    # Calculate statistics
    cov_matrix = returns.cov() * trading_days
    port_return = np.sum(returns.mean() * weights) * trading_days
    port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe_ratio = (port_return - RISK_FREE_RATE) / port_volatility
    
    return port_return, port_volatility, sharpe_ratio

def generate_random_portfolios(returns: pd.DataFrame, 
                             num_portfolios: int = 10000,
                             trading_days: int = 252) -> dict:
    """
    Generate random portfolios for efficient frontier analysis
    
    Args:
        returns: DataFrame of asset returns
        num_portfolios: Number of random portfolios to generate
        trading_days: Number of trading days in a year
        
    Returns:
        Dictionary containing:
        - 'returns': Array of portfolio returns
        - 'volatilities': Array of portfolio volatilities
        - 'weights': List of weight arrays
        - 'sharpe_ratios': Array of Sharpe ratios
    """
    results = {
        'returns': np.zeros(num_portfolios),
        'volatilities': np.zeros(num_portfolios),
        'weights': [],
        'sharpe_ratios': np.zeros(num_portfolios)
    }
    
    cov_matrix = returns.cov() * trading_days
    mean_returns = returns.mean() * trading_days
    
    for i in range(num_portfolios):
        # Generate random weights
        weights = np.random.random(len(returns.columns))
        weights /= np.sum(weights)
        
        # Calculate portfolio stats
        port_return = np.sum(mean_returns * weights)
        port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (port_return - RISK_FREE_RATE) / port_volatility
        
        # Store results
        results['returns'][i] = port_return
        results['volatilities'][i] = port_volatility
        results['weights'].append(weights)
        results['sharpe_ratios'][i] = sharpe_ratio
    
    return results