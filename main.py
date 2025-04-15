from config import *
from portfolio_analysis import (
    fetch_commodity_data, 
    calculate_portfolio_stats, 
    calculate_daily_returns,
    generate_random_portfolios
)
from monte_carlo import (
    monte_carlo_simulation,
    analyze_simulation_results,
    calculate_value_at_risk,
    calculate_expected_shortfall
)
from visualization import (
    plot_simulation_paths,
    plot_distribution,
    plot_efficient_frontier
)
from excel_interface import export_to_excel, create_interactive_dashboard
import numpy as np
import time
from typing import Dict, Tuple

def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', length: int = 50, fill: str = '█') -> None:
    """Display progress bar in console"""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total: 
        print()

def run_portfolio_analysis() -> Tuple[Dict, np.ndarray, np.ndarray]:
    """Execute complete portfolio analysis workflow"""
    results = {}
    
    try:
        # Data Collection Phase
        print("Fetching historical commodity data...")
        start_time = time.time()
        data = fetch_commodity_data(COMMODITIES, START_DATE, END_DATE)
        results['data'] = data
        print(f"Successfully fetched {len(data)} days of data for {len(COMMODITIES)} commodities")
        print(f"Time elapsed: {time.time() - start_time:.2f} seconds\n")

        # Portfolio Statistics
        print("Calculating portfolio statistics...")
        weights = np.array([1/len(COMMODITIES)] * len(COMMODITIES))
        returns = calculate_daily_returns(data)
        
        port_return, port_volatility, sharpe_ratio = calculate_portfolio_stats(returns, weights)
        results['stats'] = {
            'return': port_return,
            'volatility': port_volatility,
            'sharpe_ratio': sharpe_ratio,
            'weights': weights
        }
        
        print(f"Portfolio Allocation: {dict(zip(COMMODITIES, weights.round(4)))}\n")
        print(f"Expected Annual Return: {port_return:.2%}")
        print(f"Expected Volatility: {port_volatility:.2%}")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}\n")

        # Efficient Frontier Analysis
        print("Generating efficient frontier...")
        frontier_results = generate_random_portfolios(returns)
        plot_efficient_frontier(frontier_results['returns'], frontier_results['volatilities'])
        results['efficient_frontier'] = frontier_results

        # Monte Carlo Simulation
        print(f"\nRunning Monte Carlo simulation ({MONTE_CARLO_SIMS} iterations)...")
        sim_start = time.time()
        
        # Progress tracking callback
        def progress_callback(iter, total):
            print_progress_bar(iter, total, prefix='Progress:', suffix='Complete')
        
        portfolio_paths, price_paths = monte_carlo_simulation(
            data, 
            weights, 
            sims=MONTE_CARLO_SIMS,
            time_horizon=TIME_HORIZON,
            progress_callback=progress_callback
        )
        
        sim_time = time.time() - sim_start
        print(f"\nSimulation completed in {sim_time:.2f} seconds")
        results['simulation'] = {
            'paths': portfolio_paths,
            'price_paths': price_paths,
            'compute_time': sim_time
        }

        # Risk Analysis
        print("\nCalculating risk metrics...")
        risk_metrics = analyze_simulation_results(portfolio_paths)
        results['risk_metrics'] = risk_metrics
        
        print(f"95% Value at Risk (VaR): {risk_metrics['var_95']:.2f}")
        print(f"Expected Shortfall (CVaR): {risk_metrics['cvar_95']:.2f}")
        print(f"Best Case (95th %ile): {risk_metrics['percentile_95']:.2f}")
        print(f"Worst Case (5th %ile): {risk_metrics['percentile_5']:.2f}")

        # Visualization
        print("\nGenerating visualizations...")
        plot_simulation_paths(portfolio_paths)
        plot_distribution(portfolio_paths[-1])

        # Excel Reporting
        print("\nExporting results to Excel...")
        export_path = export_to_excel(
            data,
            portfolio_paths,
            analysis_results={
                **results['stats'],
                **results['risk_metrics']
            }
        )
        results['export_path'] = export_path
        print(f"Results exported to: {export_path}")

        return results, portfolio_paths, price_paths

    except Exception as e:
        print(f"\nError in portfolio analysis: {str(e)}")
        raise

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("COMMODITY PORTFOLIO MONTE CARLO SIMULATION")
    print("="*60 + "\n")
    
    try:
        # Run complete analysis
        results, portfolio_paths, price_paths = run_portfolio_analysis()
        
        # Uncomment to create interactive dashboard
        # print("\nCreating Excel dashboard...")
        # dashboard = create_interactive_dashboard(
        #     data=results['data'],
        #     commodities=COMMODITIES
        # )
        
        print("\nAnalysis completed successfully!")
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
    finally:
        print("\n" + "="*60)
        print("PROGRAM EXECUTION COMPLETE")
        print("="*60)

if __name__ == "__main__":
    main()