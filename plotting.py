import matplotlib.pyplot as plt
import numpy as np

class StrategyPlotter:
    """Modular plotting class for trading strategy visualizations."""
    
    def __init__(self, ticker):
        self.ticker = ticker
    
    def plot_strategy_grid(self, results, best_params, grid_dims, title_prefix, plot_type="signals"):
        """
        Generic function to create grid plots for strategy visualization.
        
        Parameters:
        - results: Results from parameter exploration
        - best_params: Best parameter combination  
        - grid_dims: Tuple (rows, cols) for subplot grid
        - title_prefix: Prefix for the plot title
        - plot_type: Either "signals" or "portfolio"
        """
        fig, axes = plt.subplots(grid_dims[0], grid_dims[1], figsize=(20, 16))
        fig.suptitle(f'{title_prefix} - {plot_type.title()} with Sharpe & Drawdown', fontsize=16)
        
        # Ensure axes is always 2D for consistent indexing
        if grid_dims[0] == 1 or grid_dims[1] == 1:
            axes = np.array(axes).reshape(grid_dims)
        
        return fig, axes
    
    def plot_single_strategy_signals(self, ax, test_data, sharpe, window, threshold=None, 
                                   best_params=None, show_legend=False, max_drawdown=None):
        """Plot trading signals for a single strategy configuration."""
        sharpe_display = f"{sharpe:.3f}" if sharpe is not None else "N/A"
        drawdown_display = f"{max_drawdown:.2%}" if max_drawdown is not None else "N/A"
        
        # Plot price and rolling mean
        ax.plot(test_data.index, test_data[f'Close_{self.ticker}'], 
               label=f'{self.ticker} Price', linewidth=1, color='gray')
        ax.plot(test_data.index, test_data['RollingMean'], 
               label='Rolling Mean', linewidth=1, color='blue')
        
        # Add threshold bands for mean reversion
        if threshold is not None:
            upper_band = test_data['RollingMean'] * (1 + threshold)
            lower_band = test_data['RollingMean'] * (1 - threshold)
            ax.fill_between(test_data.index, upper_band, lower_band, 
                           alpha=0.3, color='red', label='Threshold Bands')
            ax.plot(test_data.index, upper_band, linewidth=0.8, color='red', alpha=0.7)
            ax.plot(test_data.index, lower_band, linewidth=0.8, color='red', alpha=0.7)
        
        # Mark buy/sell signals
        self._add_trading_signals(ax, test_data)
        
        # Format title and legend
        self._format_subplot(ax, window, threshold, sharpe_display, best_params, show_legend, drawdown_display)
    
    def plot_single_strategy_portfolio(self, ax, test_data, sharpe, window, threshold=None,
                                     best_params=None, show_legend=False, max_drawdown=None):
        """Plot portfolio evolution for a single strategy configuration."""
        sharpe_display = f"{sharpe:.3f}" if sharpe is not None else "N/A"
        drawdown_display = f"{max_drawdown:.2%}" if max_drawdown is not None else "N/A"
        
        # Plot portfolio evolution
        ax.plot(test_data.index, test_data['PortfolioValue'], 
               label='Portfolio Value', linewidth=1.3, color='blue')
        
        # Mark buy/sell signals on portfolio
        self._add_portfolio_signals(ax, test_data)
        
        # Format title and legend  
        self._format_subplot(ax, window, threshold, sharpe_display, best_params, show_legend, drawdown_display)
    
    def _add_trading_signals(self, ax, test_data):
        """Add buy/sell signal markers to price plot."""
        buy_signals = test_data[test_data['Position'] == 1]
        ax.scatter(buy_signals.index, buy_signals[f'Close_{self.ticker}'], 
                  marker='^', color='green', label='Buy', s=40, alpha=0.7)
        sell_signals = test_data[test_data['Position'] == -1]
        ax.scatter(sell_signals.index, sell_signals[f'Close_{self.ticker}'], 
                  marker='v', color='red', label='Sell', s=40, alpha=0.7)
    
    def _add_portfolio_signals(self, ax, test_data):
        """Add buy/sell signal markers to portfolio plot."""
        buy_signals = test_data[test_data['Position'] == 1]
        ax.scatter(buy_signals.index, buy_signals['PortfolioValue'], 
                  marker='^', color='green', s=35, alpha=0.7)
        sell_signals = test_data[test_data['Position'] == -1]
        ax.scatter(sell_signals.index, sell_signals['PortfolioValue'], 
                  marker='v', color='red', s=35, alpha=0.7)
    
    def _format_subplot(self, ax, window, threshold, sharpe_display, best_params, show_legend, drawdown_display=None):
        """Format subplot with title, legend, and grid."""
        # Determine if this is the best parameter combination
        if threshold is not None:
            is_best = best_params == (window, threshold)
            title = f'W={window}, T={threshold:.3f}\nSharpe: {sharpe_display}'
            if drawdown_display:
                title += f'\nDrawdown: {drawdown_display}'
        else:
            is_best = best_params == window
            title = f'Window={window}\nSharpe: {sharpe_display}'
            if drawdown_display:
                title += f'\nDrawdown: {drawdown_display}'
        
        title_color = 'darkgreen' if is_best else 'black'
        ax.set_title(title, color=title_color, 
                    fontweight='bold' if is_best else 'normal')
        
        if show_legend:
            ax.legend(fontsize=8 if threshold is not None else 9)
        ax.grid(True, alpha=0.3)
    
    def create_mean_reversion_plots(self, results, best_params):
        """Create both signal and portfolio plots for mean reversion strategy."""
        windows = [10, 20, 30, 50]
        thresholds = [0.01, 0.02, 0.03, 0.05]
        
        # Create lookup dictionary for results
        results_dict = {(r['Window'], r['Threshold']): r for r in results}
        
        # Strategy signals plot
        fig, axes = self.plot_strategy_grid(
            results, best_params, (4, 4), 
            'Mean Reversion Strategy - Parameter Exploration', 'signals'
        )
        
        for i, window in enumerate(windows):
            for j, threshold in enumerate(thresholds):
                result = results_dict.get((window, threshold))
                if result is None:
                    continue
                
                self.plot_single_strategy_signals(
                    axes[i, j], result['Data'], result['Sharpe_Ratio'],
                    window, threshold, best_params, show_legend=(i == 0 and j == 0), 
                    max_drawdown=result['Max_Drawdown']
                )
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
        
        # Portfolio evolution plot
        fig, axes = self.plot_strategy_grid(
            results, best_params, (4, 4),
            'Mean Reversion Strategy - Portfolio Evolution', 'portfolio'
        )
        
        for i, window in enumerate(windows):
            for j, threshold in enumerate(thresholds):
                result = results_dict.get((window, threshold))
                if result is None:
                    continue
                
                self.plot_single_strategy_portfolio(
                    axes[i, j], result['Data'], result['Sharpe_Ratio'],
                    window, threshold, best_params, show_legend=(i == 0 and j == 0),
                    max_drawdown=result['Max_Drawdown']
                )
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
    
    def create_momentum_plots(self, results, best_params):
        """Create both signal and portfolio plots for momentum strategy."""
        windows = [10, 20, 30, 50]
        
        # Create lookup dictionary for results
        results_dict = {r['Window']: r for r in results}
        
        # Strategy signals plot
        fig, axes = self.plot_strategy_grid(
            results, best_params, (2, 2),
            'Momentum Strategy - Parameter Exploration', 'signals'
        )
        
        for i, window in enumerate(windows):
            result = results_dict.get(window)
            if result is None:
                continue
            
            row, col = i // 2, i % 2
            self.plot_single_strategy_signals(
                axes[row, col], result['Data'], result['Sharpe_Ratio'],
                window, best_params=best_params, show_legend=(i == 0),
                max_drawdown=result['Max_Drawdown']
            )
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
        
        # Portfolio evolution plot  
        fig, axes = self.plot_strategy_grid(
            results, best_params, (2, 2),
            'Momentum Strategy - Portfolio Evolution', 'portfolio'
        )
        
        for i, window in enumerate(windows):
            result = results_dict.get(window)
            if result is None:
                continue
            
            row, col = i // 2, i % 2
            self.plot_single_strategy_portfolio(
                axes[row, col], result['Data'], result['Sharpe_Ratio'],
                window, best_params=best_params, show_legend=(i == 0),
                max_drawdown=result['Max_Drawdown']
            )
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
    
    def create_strategy_comparison(self, strategy_results):
        """Create a comparison plot of different strategies."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle(f'Strategy Performance Comparison - {self.ticker}', fontsize=16)
        
        # Plot portfolio values
        for strategy_name, results in strategy_results.items():
            data = results['data']
            sharpe = results.get('sharpe')
            drawdown = None
            if isinstance(results.get('drawdown'), dict):
                drawdown = results['drawdown'].get('max_drawdown')

            label = f"{strategy_name.replace('_', ' ').title()}"
            metrics = []
            if sharpe is not None:
                metrics.append(f"Sharpe: {sharpe:.3f}")
            if drawdown is not None:
                metrics.append(f"DD: {drawdown:.2%}")
            if metrics:
                label += " (" + ", ".join(metrics) + ")"

            ax1.plot(data.index, data['PortfolioValue'], label=label, linewidth=2)
        
        ax1.set_title('Portfolio Value Evolution')
        ax1.set_ylabel('Portfolio Value')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot price with signals from first strategy
        first_strategy_data = list(strategy_results.values())[0]['data']
        ax2.plot(first_strategy_data.index, first_strategy_data[f'Close_{self.ticker}'], 
                label=f'{self.ticker} Price', linewidth=1, color='black')
        
        # Add trading signals
        self._add_trading_signals(ax2, first_strategy_data)
        
        ax2.set_title('Price Action with Trading Signals')
        ax2.set_ylabel('Price')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()