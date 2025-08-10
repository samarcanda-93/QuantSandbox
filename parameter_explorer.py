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
                
                # Calculate Sharpe ratio
                sharpe = finance_utils.calculate_sharpe_ratio(test_data)
                
                # Store results
                results.append({
                    'Window': window,
                    'Threshold': threshold,
                    'Sharpe_Ratio': sharpe if sharpe is not None else np.nan,
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
            
            # Calculate Sharpe ratio
            sharpe = finance_utils.calculate_sharpe_ratio(test_data)
            
            # Store results
            results.append({
                'Window': window,
                'Sharpe_Ratio': sharpe if sharpe is not None else np.nan,
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
            {'Window': r['Window'], 'Threshold': r['Threshold'], 'Sharpe_Ratio': r['Sharpe_Ratio']} 
            for r in results
        ])
        
        print("\n" + "="*60)
        print("MEAN REVERSION STRATEGY - SHARPE RATIO RESULTS")
        print("="*60)
        print(results_df.pivot(index='Window', columns='Threshold', values='Sharpe_Ratio').round(4))
        
        # Display best parameter combination
        if best_params:
            print(f"\n🏆 BEST PARAMETER COMBINATION:")
            print(f"   Window: {best_params[0]}, Threshold: {best_params[1]:.3f}")
            print(f"   Sharpe Ratio: {best_sharpe:.4f}")
        else:
            print(f"\n❌ Unable to determine best parameters (all strategies failed)")
        print("="*60)
    
    def display_momentum_results(self, results, best_params, best_sharpe):
        """Display momentum parameter exploration results."""
        results_df = pd.DataFrame([
            {'Window': r['Window'], 'Sharpe_Ratio': r['Sharpe_Ratio']} 
            for r in results
        ])
        
        print("\n" + "="*50)
        print("MOMENTUM STRATEGY - SHARPE RATIO RESULTS")
        print("="*50)
        print(results_df.set_index('Window')['Sharpe_Ratio'].round(4).to_string())
        
        # Display best parameter combination
        if best_params:
            print(f"\n🏆 BEST MOMENTUM PARAMETER:")
            print(f"   Window: {best_params}")
            print(f"   Sharpe Ratio: {best_sharpe:.4f}")
        else:
            print(f"\n❌ Unable to determine best momentum parameters")
        print("="*50)
    
    def get_user_parameters(self):
        """Get custom parameters from user for basic comparison."""
        print("\n" + "="*50)
        print("STRATEGY PARAMETER CONFIGURATION")
        print("="*50)
        
        # Get momentum parameters
        print("\n📈 Momentum Strategy Parameters:")
        momentum_window = self._get_user_input(
            "Rolling window size (default: 20): ", 
            default=20, 
            param_type=int,
            valid_range=(5, 200)
        )
        
        # Get mean reversion parameters  
        print("\n📊 Mean Reversion Strategy Parameters:")
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
                    print(f"❌ Value must be between {valid_range[0]} and {valid_range[1]}")
                    continue
                    
                return value
                
            except ValueError:
                print(f"❌ Invalid input. Please enter a valid {param_type.__name__}")
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
        print(f"📈 Momentum Strategy Sharpe Ratio: {momentum_sharpe:.4f}" if momentum_sharpe else "📈 Momentum Strategy Sharpe Ratio: Unable to calculate")

        # Strategy 2: Mean Reversion Strategy  
        mean_reversion_data = strategies.mean_reversion_strategy(
            self.data.copy(), window=mr_window, threshold=mr_threshold, ticker=self.ticker
        )
        mean_reversion_data = finance_utils.simulate_portfolio(
            mean_reversion_data, f"Mean Reversion (W={mr_window}, T={mr_threshold:.3f})", ticker=self.ticker
        )
        mean_reversion_sharpe = finance_utils.calculate_sharpe_ratio(mean_reversion_data)
        print(f"📊 Mean Reversion Strategy Sharpe Ratio: {mean_reversion_sharpe:.4f}" if mean_reversion_sharpe else "📊 Mean Reversion Strategy Sharpe Ratio: Unable to calculate")
        
        # Display winner
        self._display_strategy_winner(momentum_sharpe, mean_reversion_sharpe)
        
        return {
            'momentum': {'data': momentum_data, 'sharpe': momentum_sharpe, 'params': {'window': momentum_window}},
            'mean_reversion': {'data': mean_reversion_data, 'sharpe': mean_reversion_sharpe, 'params': {'window': mr_window, 'threshold': mr_threshold}}
        }
    
    def _display_strategy_winner(self, momentum_sharpe, mean_reversion_sharpe):
        """Display which strategy performed better."""
        print("\n" + "="*50)
        if momentum_sharpe is None and mean_reversion_sharpe is None:
            print("❌ Unable to determine winner - both strategies failed")
        elif momentum_sharpe is None:
            print("🏆 WINNER: Mean Reversion Strategy (Momentum failed)")
        elif mean_reversion_sharpe is None:
            print("🏆 WINNER: Momentum Strategy (Mean Reversion failed)")
        elif momentum_sharpe > mean_reversion_sharpe:
            print(f"🏆 WINNER: Momentum Strategy (Sharpe: {momentum_sharpe:.4f} vs {mean_reversion_sharpe:.4f})")
        elif mean_reversion_sharpe > momentum_sharpe:
            print(f"🏆 WINNER: Mean Reversion Strategy (Sharpe: {mean_reversion_sharpe:.4f} vs {momentum_sharpe:.4f})")
        else:
            print("🤝 TIE: Both strategies have equal Sharpe ratios")
        print("="*50)