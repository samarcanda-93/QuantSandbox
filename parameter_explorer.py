import pandas as pd
import numpy as np
import strategies
import finance_utils

class ParameterExplorer:
    """Class to handle parameter exploration and optimization for trading strategies."""
    
    def __init__(self, data, ticker):
        self.data = data
        self.ticker = ticker
        
    def explore_mean_reversion_parameters(self, windows=None, thresholds=None):
        """
        Explore different parameter combinations for mean reversion strategy.
        
        Parameters:
        - windows: List of window sizes to test (default: [10, 20, 30, 50])
        - thresholds: List of threshold values to test (default: [0.01, 0.02, 0.03, 0.05])
        
        Returns:
        - tuple: (results_list, best_params, best_sharpe)
        """
        if windows is None:
            windows = [10, 20, 30, 50]
        if thresholds is None:
            thresholds = [0.01, 0.02, 0.03, 0.05]
            
        results = []
        best_sharpe = -np.inf
        best_params = None
        
        print("Exploring mean reversion parameters...")
        total_combinations = len(windows) * len(thresholds)
        current_combination = 0
        
        for window in windows:
            for threshold in thresholds:
                current_combination += 1
                print(f"Testing combination {current_combination}/{total_combinations}: Window={window}, Threshold={threshold:.3f}")
                
                # Apply mean reversion strategy with current parameters
                test_data = strategies.mean_reversion_strategy(
                    self.data.copy(), 
                    window=window, 
                    threshold=threshold, 
                    ticker=self.ticker
                )
                
                # Simulate portfolio
                test_data = finance_utils.simulate_portfolio(
                    test_data, 
                    f"Mean Reversion (W={window}, T={threshold})", 
                    ticker=self.ticker
                )
                
                # Calculate Sharpe ratio and drawdown
                sharpe = finance_utils.calculate_sharpe_ratio(test_data)
                drawdown_metrics = finance_utils.calculate_max_drawdown(test_data)
                
                # Store results
                results.append({
                    'Window': window,
                    'Threshold': threshold,
                    'Sharpe_Ratio': sharpe if sharpe is not None else np.nan,
                    'Max_Drawdown': drawdown_metrics['max_drawdown'],
                    'Data': test_data
                })
                
                # Track best parameters
                if sharpe is not None and sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_params = (window, threshold)
        
        return results, best_params, best_sharpe
    
    def explore_momentum_parameters(self, windows=None):
        """
        Explore different parameter combinations for momentum strategy.
        
        Parameters:
        - windows: List of window sizes to test (default: [10, 20, 30, 50])
        
        Returns:
        - tuple: (results_list, best_params, best_sharpe)
        """
        if windows is None:
            windows = [10, 20, 30, 50]
            
        results = []
        best_sharpe = -np.inf
        best_params = None
        
        print("Exploring momentum parameters...")
        
        for i, window in enumerate(windows, 1):
            print(f"Testing momentum window {i}/{len(windows)}: Window={window}")
            
            # Apply momentum strategy with current parameters
            test_data = strategies.simple_momentum_strategy(
                self.data.copy(), 
                window=window, 
                ticker=self.ticker
            )
            
            # Simulate portfolio
            test_data = finance_utils.simulate_portfolio(
                test_data, 
                f"Momentum (W={window})", 
                ticker=self.ticker
            )
            
            # Calculate Sharpe ratio and drawdown
            sharpe = finance_utils.calculate_sharpe_ratio(test_data)
            drawdown_metrics = finance_utils.calculate_max_drawdown(test_data)
            
            # Store results
            results.append({
                'Window': window,
                'Sharpe_Ratio': sharpe if sharpe is not None else np.nan,
                'Max_Drawdown': drawdown_metrics['max_drawdown'],
                'Data': test_data
            })
            
            # Track best parameters
            if sharpe is not None and sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = window
        
        return results, best_params, best_sharpe
    
    def display_mean_reversion_results(self, results, best_params, best_sharpe):
        """Display mean reversion parameter exploration results."""
        results_df = pd.DataFrame([
            {'Window': r['Window'], 'Threshold': r['Threshold'], 'Sharpe_Ratio': r['Sharpe_Ratio'], 'Max_Drawdown': r['Max_Drawdown']} 
            for r in results
        ])
        
        print("\n" + "="*70)
        print("MEAN REVERSION STRATEGY - PERFORMANCE RESULTS")
        print("="*70)
        print("SHARPE RATIO:")
        print(results_df.pivot(index='Window', columns='Threshold', values='Sharpe_Ratio').round(4))
        
        print("\nMAXIMUM DRAWDOWN:")
        drawdown_pivot = results_df.pivot(index='Window', columns='Threshold', values='Max_Drawdown').round(4)
        print(drawdown_pivot)
        
        # Display best parameter combination with drawdown
        if best_params:
            best_result = next(r for r in results if r['Window'] == best_params[0] and r['Threshold'] == best_params[1])
            print(f"\nBEST PARAMETER COMBINATION:")
            print(f"   Window: {best_params[0]}, Threshold: {best_params[1]:.3f}")
            print(f"   Sharpe Ratio: {best_sharpe:.4f}")
            print(f"   Max Drawdown: {best_result['Max_Drawdown']:.2%}" if best_result['Max_Drawdown'] else "   Max Drawdown: N/A")
        else:
            print(f"\nERROR: Unable to determine best parameters (all strategies failed)")
        print("="*70)
    
    def display_momentum_results(self, results, best_params, best_sharpe):
        """Display momentum parameter exploration results."""
        results_df = pd.DataFrame([
            {'Window': r['Window'], 'Sharpe_Ratio': r['Sharpe_Ratio'], 'Max_Drawdown': r['Max_Drawdown']} 
            for r in results
        ])
        
        print("\n" + "="*60)
        print("MOMENTUM STRATEGY - PERFORMANCE RESULTS")
        print("="*60)
        print("SHARPE RATIO & MAX DRAWDOWN:")
        display_df = results_df.set_index('Window')[['Sharpe_Ratio', 'Max_Drawdown']].round(4)
        display_df['Max_Drawdown'] = display_df['Max_Drawdown'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")
        print(display_df.to_string())
        
        # Display best parameter combination with drawdown
        if best_params:
            best_result = next(r for r in results if r['Window'] == best_params)
            print(f"\nBEST MOMENTUM PARAMETER:")
            print(f"   Window: {best_params}")
            print(f"   Sharpe Ratio: {best_sharpe:.4f}")
            print(f"   Max Drawdown: {best_result['Max_Drawdown']:.2%}" if best_result['Max_Drawdown'] else "   Max Drawdown: N/A")
        else:
            print(f"\nERROR: Unable to determine best momentum parameters")
        print("="*60)
    
    def get_user_parameters(self):
        """Get custom parameters from user for basic comparison."""
        print("\n" + "="*50)
        print("STRATEGY PARAMETER CONFIGURATION")
        print("="*50)
        
        # Get momentum parameters
        print("\nMomentum Strategy Parameters:")
        momentum_window = self._get_user_input(
            "Rolling window size (default: 20): ", 
            default=20, 
            param_type=int,
            valid_range=(5, 200)
        )
        
        # Get mean reversion parameters  
        print("\nMean Reversion Strategy Parameters:")
        mr_window = self._get_user_input(
            "Rolling window size (default: 20): ",
            default=20,
            param_type=int, 
            valid_range=(5, 200)
        )
        
        mr_threshold = self._get_user_input(
            "Threshold percentage (0.01 = 1%, default: 0.02): ",
            default=0.02,
            param_type=float,
            valid_range=(0.001, 0.1)
        )
        
        return {
            'momentum_window': momentum_window,
            'mr_window': mr_window,
            'mr_threshold': mr_threshold
        }
    
    def _get_user_input(self, prompt, default, param_type, valid_range=None):
        """Helper function to get and validate user input."""
        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input:
                    return default
                
                value = param_type(user_input)
                
                if valid_range and not (valid_range[0] <= value <= valid_range[1]):
                    print(f"ERROR: Value must be between {valid_range[0]} and {valid_range[1]}")
                    continue
                    
                return value
                
            except ValueError:
                print(f"ERROR: Invalid input. Please enter a valid {param_type.__name__}")
            except (EOFError, KeyboardInterrupt):
                print(f"\nUsing default: {default}")
                return default
    
    def run_basic_strategy_comparison(self, custom_params=None):
        """Run basic comparison of strategies with user-specified or default parameters."""
        if custom_params is None:
            # Use defaults
            momentum_window = 20
            mr_window = 20
            mr_threshold = 0.02
            print("Running basic strategy comparison with default parameters...")
        else:
            # Use custom parameters
            momentum_window = custom_params['momentum_window']
            mr_window = custom_params['mr_window'] 
            mr_threshold = custom_params['mr_threshold']
            print(f"\nRunning basic strategy comparison with custom parameters:")
            print(f"  Momentum Window: {momentum_window}")
            print(f"  Mean Reversion Window: {mr_window}")
            print(f"  Mean Reversion Threshold: {mr_threshold:.3f} ({mr_threshold*100:.1f}%)")
        
        print("\n" + "="*50)
        print("STRATEGY PERFORMANCE RESULTS")
        print("="*50)
        
        # Strategy 1: Momentum Strategy
        momentum_data = strategies.simple_momentum_strategy(
            self.data.copy(), window=momentum_window, ticker=self.ticker
        )
        momentum_data = finance_utils.simulate_portfolio(
            momentum_data, f"Momentum (W={momentum_window})", ticker=self.ticker
        )
        momentum_sharpe = finance_utils.calculate_sharpe_ratio(momentum_data, print_rate_info=True)
        momentum_drawdown = finance_utils.calculate_max_drawdown(momentum_data)
        print(f"Momentum Strategy:")
        print(f"   Sharpe Ratio: {momentum_sharpe:.4f}" if momentum_sharpe else "   Sharpe Ratio: Unable to calculate")
        print(f"   Max Drawdown: {momentum_drawdown['max_drawdown']:.2%}" if momentum_drawdown['max_drawdown'] else "   Max Drawdown: N/A")

        # Strategy 2: Mean Reversion Strategy  
        mean_reversion_data = strategies.mean_reversion_strategy(
            self.data.copy(), window=mr_window, threshold=mr_threshold, ticker=self.ticker
        )
        mean_reversion_data = finance_utils.simulate_portfolio(
            mean_reversion_data, f"Mean Reversion (W={mr_window}, T={mr_threshold:.3f})", ticker=self.ticker
        )
        mean_reversion_sharpe = finance_utils.calculate_sharpe_ratio(mean_reversion_data)
        mean_reversion_drawdown = finance_utils.calculate_max_drawdown(mean_reversion_data)
        print(f"Mean Reversion Strategy:")
        print(f"   Sharpe Ratio: {mean_reversion_sharpe:.4f}" if mean_reversion_sharpe else "   Sharpe Ratio: Unable to calculate")
        print(f"   Max Drawdown: {mean_reversion_drawdown['max_drawdown']:.2%}" if mean_reversion_drawdown['max_drawdown'] else "   Max Drawdown: N/A")
        
        # Display winner
        self._display_strategy_winner(momentum_sharpe, mean_reversion_sharpe)
        
        return {
            'momentum': {'data': momentum_data, 'sharpe': momentum_sharpe, 'drawdown': momentum_drawdown, 'params': {'window': momentum_window}},
            'mean_reversion': {'data': mean_reversion_data, 'sharpe': mean_reversion_sharpe, 'drawdown': mean_reversion_drawdown, 'params': {'window': mr_window, 'threshold': mr_threshold}}
        }
    
    def _display_strategy_winner(self, momentum_sharpe, mean_reversion_sharpe):
        """Display which strategy performed better."""
        print("\n" + "="*50)
        if momentum_sharpe is None and mean_reversion_sharpe is None:
            print("ERROR: Unable to determine winner - both strategies failed")
        elif momentum_sharpe is None:
            print("WINNER: Mean Reversion Strategy (Momentum failed)")
        elif mean_reversion_sharpe is None:
            print("WINNER: Momentum Strategy (Mean Reversion failed)")
        elif momentum_sharpe > mean_reversion_sharpe:
            print(f"WINNER: Momentum Strategy (Sharpe: {momentum_sharpe:.4f} vs {mean_reversion_sharpe:.4f})")
        elif mean_reversion_sharpe > momentum_sharpe:
            print(f"WINNER: Mean Reversion Strategy (Sharpe: {mean_reversion_sharpe:.4f} vs {momentum_sharpe:.4f})")
        else:
            print("TIE: Both strategies have equal Sharpe ratios")
        print("="*50)