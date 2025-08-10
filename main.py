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
import report_generator
import pdf_generator
import finance_utils

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
        
        # Offer to generate PDF report
        report_generator.prompt_for_report_generation('basic', results=basic_results, ticker=ticker)
        
        # Print end-of-run recommendation based on latest signals
        try:
            print("\nToday's suggestion based on latest signals:")
            suggestion_printed = False
            # Prefer the strategy with higher Sharpe if both available
            strat_order = sorted(basic_results.items(), key=lambda kv: (kv[1]['sharpe'] if kv[1]['sharpe'] is not None else float('-inf')), reverse=True)
            for _, strat_data in strat_order:
                rec = finance_utils.latest_trade_recommendation(strat_data['data'], ticker=ticker)
                if rec and rec.get('as_of_date') is not None:
                    date_str = rec['as_of_date'].strftime('%Y-%m-%d') if hasattr(rec['as_of_date'], 'strftime') else str(rec['as_of_date'])
                    price_str = f" at {rec['price']:.2f}" if rec.get('price') is not None else ""
                    print(f"  {rec['action']} ({rec['state']}) as of {date_str}{price_str}")
                    suggestion_printed = True
                    break
            if suggestion_printed:
                print("  Note: This is not financial advice.")
        except Exception as e:
            print(f"Could not compute suggestion: {e}")

        print("\nBasic analysis complete!")
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
    
    # Offer to generate comprehensive PDF report
    report_generator.prompt_for_report_generation('full', 
                                                  mr_results=mr_results, 
                                                  mom_results=mom_results,
                                                  mr_best_params=mr_best_params, 
                                                  mom_best_params=mom_best_params, 
                                                  ticker=ticker)
    
    # End-of-run recommendation for full exploration: use best Sharpe strategies
    try:
        print("\nToday's suggestion based on latest signals:")
        best_mr = next((r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1]), None) if mr_best_params else None
        best_mom = next((r for r in mom_results if r['Window'] == mom_best_params), None) if mom_best_params else None

        candidates = []
        if best_mr:
            candidates.append(('Mean Reversion', best_mr))
        if best_mom:
            candidates.append(('Momentum', best_mom))

        # Sort by Sharpe descending
        candidates.sort(key=lambda x: (x[1]['Sharpe_Ratio'] if x[1]['Sharpe_Ratio'] is not None else float('-inf')), reverse=True)

        suggestion_printed = False
        for name, res in candidates:
            rec = finance_utils.latest_trade_recommendation(res['Data'], ticker=ticker)
            if rec and rec.get('as_of_date') is not None:
                date_str = rec['as_of_date'].strftime('%Y-%m-%d') if hasattr(rec['as_of_date'], 'strftime') else str(rec['as_of_date'])
                price_str = f" at {rec['price']:.2f}" if rec.get('price') is not None else ""
                print(f"  {name}: {rec['action']} ({rec['state']}) as of {date_str}{price_str}")
                suggestion_printed = True
                break
        if suggestion_printed:
            print("  Note: This is not financial advice.")
    except Exception as e:
        print(f"Could not compute suggestion: {e}")

    print("\nAnalysis complete! All plots have been displayed.")

if __name__ == "__main__":
    main()