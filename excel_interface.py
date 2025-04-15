import xlwings as xw
import pandas as pd
import numpy as np
import os
from typing import Union, Optional
from datetime import datetime
from config import COMMODITIES  # Import from config

# Constants
DEFAULT_OUTPUT_DIR = 'outputs'
DEFAULT_FILENAME = 'portfolio_analysis.xlsx'

def export_to_excel(
    data: pd.DataFrame,
    portfolio_paths: np.ndarray,
    analysis_results: Optional[dict] = None,
    output_file: Optional[str] = None,
    include_paths: bool = True
) -> str:
    """
    Export simulation results to Excel with comprehensive reporting
    
    Args:
        data: Historical price data
        portfolio_paths: Simulated portfolio paths
        analysis_results: Dictionary of analysis metrics (optional)
        output_file: Custom output file path (optional)
        include_paths: Whether to include full simulation paths
        
    Returns:
        Path to the created Excel file
        
    Raises:
        ValueError: If input validation fails
        PermissionError: If file cannot be written
    """
    # Validate inputs
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be a pandas DataFrame")
    if not isinstance(portfolio_paths, np.ndarray):
        raise ValueError("Portfolio paths must be a numpy array")
    
    # Set default output file if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(DEFAULT_OUTPUT_DIR, f"portfolio_analysis_{timestamp}.xlsx")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    try:
        # Create DataFrames for export
        final_values = portfolio_paths[-1]
        
        # Basic results DataFrame
        results_df = pd.DataFrame({
            'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max',
                      '5% Percentile', '95% Percentile', 'VaR (95%)', 'CVaR (95%)'],
            'Value': [
                np.mean(final_values),
                np.median(final_values),
                np.std(final_values),
                np.min(final_values),
                np.max(final_values),
                np.percentile(final_values, 5),
                np.percentile(final_values, 95),
                np.percentile(final_values, 5),  # VaR at 95%
                final_values[final_values <= np.percentile(final_values, 5)].mean()  # CVaR
            ]
        })
        
        # Additional analysis if provided
        if analysis_results:
            analysis_df = pd.DataFrame(list(analysis_results.items()), columns=['Metric', 'Value'])
        else:
            analysis_df = pd.DataFrame()
        
        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Historical data
            data.to_excel(writer, sheet_name='Historical Data')
            
            # Results summary
            results_df.to_excel(writer, sheet_name='Summary Results', index=False)
            
            # Additional analysis
            if not analysis_df.empty:
                analysis_df.to_excel(writer, sheet_name='Detailed Analysis', index=False)
            
            # Simulation paths
            if include_paths:
                pd.DataFrame(portfolio_paths).to_excel(
                    writer, sheet_name='Simulation Paths', index=False)
                
                # Add basic statistics to paths sheet
                writer.sheets['Simulation Paths'].cell(row=1, column=portfolio_paths.shape[1]+2).value = 'Statistics'
                for i, (metric, value) in enumerate(zip(results_df['Metric'], results_df['Value']), start=2):
                    writer.sheets['Simulation Paths'].cell(row=i, column=portfolio_paths.shape[1]+2).value = metric
                    writer.sheets['Simulation Paths'].cell(row=i, column=portfolio_paths.shape[1]+3).value = value
            
            # Add charts if xlwings is available
            try:
                wb = writer.book
                if include_paths:
                    # Add chart for simulation paths
                    sheet = wb['Simulation Paths']
                    chart = xw.Chart(sheet)
                    chart.set_source_data(sheet.range((2, 1), (portfolio_paths.shape[0]+1, min(10, portfolio_paths.shape[1])))
                    chart.chart_type = 'line'
                    chart.name = "Simulation Paths"
                    sheet.add_chart(chart, "K2")
            except Exception as e:
                print(f"Could not create Excel charts: {e}")
        
        print(f"Successfully exported results to {output_file}")
        return output_file
    
    except Exception as e:
        raise PermissionError(f"Failed to write Excel file: {str(e)}")

def create_interactive_dashboard(
    data: Optional[pd.DataFrame] = None,
    commodities: Optional[list] = None,
    template_path: Optional[str] = None
) -> xw.Book:
    """
    Create an interactive Excel dashboard with xlwings
    
    Args:
        data: Optional historical data to pre-load
        commodities: List of commodity symbols
        template_path: Path to Excel template (optional)
    
    Returns:
        xlwings Book object
        
    Raises:
        FileNotFoundError: If template is specified but not found
    """
    if commodities is None:
        commodities = COMMODITIES
    
    try:
        # Create or open workbook
        if template_path:
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template file not found: {template_path}")
            wb = xw.Book(template_path)
        else:
            wb = xw.Book()
        
        # Set up dashboard sheet
        if "Dashboard" in [sheet.name for sheet in wb.sheets]:
            sheet = wb.sheets["Dashboard"]
        else:
            sheet = wb.sheets.add("Dashboard")
        
        # Clear existing content
        sheet.clear()
        
        # Add dashboard title and headers
        sheet.range("A1").value = "Commodity Portfolio Monte Carlo Simulation"
        sheet.range("A1").font.bold = True
        sheet.range("A1").font.size = 16
        
        # Add input section
        sheet.range("A3").value = "Portfolio Weights"
        sheet.range("A3").font.bold = True
        
        for i, commodity in enumerate(commodities, start=4):
            sheet.range(f"A{i}").value = f"{commodity}:"
            sheet.range(f"B{i}").value = 1/len(commodities)  # Equal weights by default
            sheet.range(f"B{i}").number_format = "0.00%"
        
        # Add simulation parameters
        param_row = len(commodities) + 5
        sheet.range(f"A{param_row}").value = "Simulation Parameters"
        sheet.range(f"A{param_row}").font.bold = True
        sheet.range(f"A{param_row+1}").value = "Number of Simulations:"
        sheet.range(f"B{param_row+1}").value = 1000
        sheet.range(f"A{param_row+2}").value = "Time Horizon (days):"
        sheet.range(f"B{param_row+2}").value = 252
        
        # Add buttons
        button_row = param_row + 4
        run_button = sheet.range(f"A{button_row}")
        run_button.value = "Run Simulation"
        run_button.color = (0, 120, 215)  # Blue color
        run_button.font.color = (255, 255, 255)  # White text
        
        export_button = sheet.range(f"C{button_row}")
        export_button.value = "Export Results"
        export_button.color = (50, 150, 50)  # Green color
        export_button.font.color = (255, 255, 255)  # White text
        
        # Add output area
        output_row = button_row + 2
        sheet.range(f"A{output_row}").value = "Simulation Results"
        sheet.range(f"A{output_row}").font.bold = True
        
        # Add VBA macros (if template didn't provide them)
        if not template_path:
            try:
                # Simple macro to show message (would need full VBA editor to implement actual functionality)
                macro_code = """
                Sub RunSimulation()
                    MsgBox "Simulation would run here in a full implementation"
                End Sub
                """
                wb.macro("RunSimulation").code = macro_code
                run_button.api.OnAction = "RunSimulation"
            except:
                print("Note: Could not add VBA macros. For full functionality, create macros manually.")
        
        # Pre-load data if provided
        if data is not None:
            if "Historical Data" in [sheet.name for sheet in wb.sheets]:
                data_sheet = wb.sheets["Historical Data"]
            else:
                data_sheet = wb.sheets.add("Historical Data", after=sheet)
            data_sheet.range("A1").value = data
        
        print("Interactive dashboard created in Excel")
        return wb
    
    except Exception as e:
        raise RuntimeError(f"Failed to create dashboard: {str(e)}")

def open_excel_file(file_path: str) -> xw.Book:
    """
    Open an existing Excel file with xlwings
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        xlwings Book object
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")
    return xw.Book(file_path)