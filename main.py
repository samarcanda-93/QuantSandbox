#!/usr/bin/env python3
"""
QuantSandbox - Main execution script for trading strategy backtesting.

This is a streamlined version that uses modular components for
clean separation of concerns.
"""

# Import our modular components
import ai_utils
import data_loader
import parameter_explorer
import plotting

def main():
    """Main execution function."""
    # Check API setup on startup
    ai_utils.check_api_setup()
    
    # Load and prepare data
    ticker, data = data_loader.load_and_prepare_data()
    
    # Initialize parameter explorer
    explorer = parameter_explorer.ParameterExplorer(data, ticker)
    
    # Decide what level of analysis to run
    print("\nChoose analysis level:")
    print("1. Basic comparison with custom parameters")
    print("2. Full parameter exploration with visualizations")
    
    try:
        choice = input("Enter choice (1 or 2, default=2): ").strip()
        if not choice:
            choice = "2"
    except (EOFError, KeyboardInterrupt):
        choice = "2"
    
    if choice == "1":
        # Get user parameters for basic comparison
        custom_params = explorer.get_user_parameters()
        basic_results = explorer.run_basic_strategy_comparison(custom_params)
        
        # Optional: offer to show quick comparison plot
        try:
            show_plot = input("\nShow comparison plot? (y/N): ").strip().lower()
            if show_plot in ['y', 'yes']:
                plotter = plotting.StrategyPlotter(ticker)
                plotter.create_strategy_comparison(basic_results)
        except (EOFError, KeyboardInterrupt):
            pass
        
        print("\n✅ Basic analysis complete!")
        return
    
    print("\nRunning full parameter exploration...")
    
    # Run parameter exploration
    mr_results, mr_best_params, mr_best_sharpe = explorer.explore_mean_reversion_parameters()
    mom_results, mom_best_params, mom_best_sharpe = explorer.explore_momentum_parameters()
    
    # Display results
    explorer.display_mean_reversion_results(mr_results, mr_best_params, mr_best_sharpe)
    explorer.display_momentum_results(mom_results, mom_best_params, mom_best_sharpe)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    plotter = plotting.StrategyPlotter(ticker)
    plotter.create_mean_reversion_plots(mr_results, mr_best_params)
    plotter.create_momentum_plots(mom_results, mom_best_params)
    
    print("\n✅ Analysis complete! All plots have been displayed.")

if __name__ == "__main__":
    main()