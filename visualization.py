import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Define risk-free rate (can be overridden by config)
RISK_FREE_RATE = 0.01  # Default value, can be updated from config

def plot_simulation_paths(portfolio_paths, num_paths=100):
    """Plot Monte Carlo simulation paths
    
    Args:
        portfolio_paths (np.ndarray): 2D array of portfolio paths.
        num_paths (int): Number of paths to plot.
    """
    # Ensure portfolio_paths is a NumPy array
    portfolio_paths = np.array(portfolio_paths)
    
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_paths[:, :num_paths], linewidth=1)
    plt.title('Monte Carlo Simulation of Portfolio Value')
    plt.xlabel('Trading Days')
    plt.ylabel('Portfolio Value')
    plt.grid(True)
    plt.show()

def plot_distribution(final_values):
    """Plot distribution of final portfolio values
    
    Args:
        final_values (np.ndarray or pd.Series): Final portfolio values.
    """
    # Ensure final_values is a NumPy array
    final_values = np.array(final_values)
    
    plt.figure(figsize=(12, 6))
    sns.histplot(final_values, kde=True, bins=50)
    plt.title('Distribution of Final Portfolio Values')
    plt.xlabel('Portfolio Value')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()

def plot_efficient_frontier(returns, volatilities, risk_free_rate=None):
    """Plot efficient frontier
    
    Args:
        returns (np.ndarray): Expected returns of portfolios.
        volatilities (np.ndarray): Volatilities of portfolios.
        risk_free_rate (float, optional): Risk-free rate for Sharpe ratio.
    """
    # Use provided risk-free rate or module default
    if risk_free_rate is None:
        risk_free_rate = RISK_FREE_RATE
    
    # Ensure returns and volatilities are NumPy arrays
    returns = np.array(returns)
    volatilities = np.array(volatilities)
    
    plt.figure(figsize=(12, 6))
    scatter = plt.scatter(
        volatilities, 
        returns, 
        c=(returns - risk_free_rate) / volatilities, 
        cmap='viridis'
    )
    plt.colorbar(scatter, label='Sharpe Ratio')
    plt.title('Efficient Frontier')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.grid(True)
    plt.show()