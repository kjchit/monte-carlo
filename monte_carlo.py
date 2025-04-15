import numpy as np
import pandas as pd
from typing import Tuple
from config import RISK_FREE_RATE, TIME_HORIZON, MONTE_CARLO_SIMS
from portfolio_analysis import calculate_daily_returns

def monte_carlo_simulation(
    data: pd.DataFrame,
    weights: np.ndarray,
    sims: int = MONTE_CARLO_SIMS,
    time_horizon: int = TIME_HORIZON,
    random_seed: int = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform Monte Carlo simulation for commodity portfolio
    
    Args:
        data: Historical price data (DataFrame)
        weights: Portfolio allocation weights (array)
        sims: Number of simulations (default from config)
        time_horizon: Simulation period in days (default from config)
        random_seed: Optional random seed for reproducibility
        
    Returns:
        Tuple containing:
        - portfolio_paths: Array of simulated portfolio paths (shape: time_horizon × sims)
        - price_paths: Array of simulated price paths (shape: n_assets × time_horizon × sims)
        
    Raises:
        ValueError: If input validation fails
    """
    # Input validation
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be a pandas DataFrame")
    if len(weights) != data.shape[1]:
        raise ValueError("Number of weights must match number of assets")
    if not np.isclose(np.sum(weights), 1, rtol=0.01):
        raise ValueError("Weights must sum to 1 (±1% tolerance)")
    
    # Set random seed if provided
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Calculate daily returns and statistics
    returns = calculate_daily_returns(data)
    mean_returns = returns.mean().values
    cov_matrix = returns.cov().values
    
    try:
        # Cholesky decomposition for correlated random numbers
        chol = np.linalg.cholesky(cov_matrix)
    except np.linalg.LinAlgError:
        # Handle non-positive definite covariance matrix
        eigvals, eigvecs = np.linalg.eigh(cov_matrix)
        eigvals[eigvals < 0] = 0  # Set negative eigenvalues to zero
        cov_matrix = eigvecs @ np.diag(eigvals) @ eigvecs.T
        chol = np.linalg.cholesky(cov_matrix)
    
    # Generate correlated random numbers
    random_numbers = np.random.normal(size=(time_horizon, sims, len(weights)))
    correlated_returns = np.tensordot(chol, random_numbers, axes=1)
    daily_returns = mean_returns.reshape(-1, 1, 1) + correlated_returns
    
    # Calculate price paths
    last_prices = data.iloc[-1].values
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = last_prices
    
    for t in range(1, time_horizon):
        price_paths[t] = price_paths[t-1] * np.exp(daily_returns[t])
    
    # Calculate portfolio values
    portfolio_paths = np.sum(price_paths * weights.reshape(-1, 1, 1), axis=0)
    
    return portfolio_paths, price_paths

def calculate_value_at_risk(portfolio_paths: np.ndarray, 
                          confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) from simulation results
    
    Args:
        portfolio_paths: Simulated portfolio paths
        confidence_level: VaR confidence level (default: 95%)
        
    Returns:
        VaR at specified confidence level
    """
    final_values = portfolio_paths[-1]
    return np.percentile(final_values, 100 * (1 - confidence_level))

def calculate_expected_shortfall(portfolio_paths: np.ndarray,
                               confidence_level: float = 0.95) -> float:
    """
    Calculate Expected Shortfall (CVaR) from simulation results
    
    Args:
        portfolio_paths: Simulated portfolio paths
        confidence_level: ES confidence level (default: 95%)
        
    Returns:
        Expected shortfall at specified confidence level
    """
    final_values = portfolio_paths[-1]
    var = calculate_value_at_risk(portfolio_paths, confidence_level)
    return final_values[final_values <= var].mean()

def analyze_simulation_results(portfolio_paths: np.ndarray) -> dict:
    """
    Generate comprehensive statistics from simulation results
    
    Args:
        portfolio_paths: Simulated portfolio paths
        
    Returns:
        Dictionary containing various risk/return statistics
    """
    final_values = portfolio_paths[-1]
    
    return {
        'mean': np.mean(final_values),
        'median': np.median(final_values),
        'std_dev': np.std(final_values),
        'min': np.min(final_values),
        'max': np.max(final_values),
        'var_95': calculate_value_at_risk(portfolio_paths),
        'cvar_95': calculate_expected_shortfall(portfolio_paths),
        'percentile_5': np.percentile(final_values, 5),
        'percentile_25': np.percentile(final_values, 25),
        'percentile_75': np.percentile(final_values, 75),
        'percentile_95': np.percentile(final_values, 95),
    }