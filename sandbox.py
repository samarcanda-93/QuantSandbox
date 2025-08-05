import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import strategies
import utils

ticker = 'BTC-USD' 
data = yf.download(ticker, start="2024-06-01", end="2025-07-01", auto_adjust=False)

# Strategy 1: Momentum Strategy
momentum_data = strategies.simple_momentum_strategy(data.copy(), ticker=ticker)

# Strategy 2: Mean Reversion Strategy  
mean_reversion_data = strategies.mean_reversion_strategy(data.copy(), ticker=ticker)

# Parameter exploration for mean reversion strategy

# Define parameter ranges to test
windows = [10, 20, 30, 50]
thresholds = [0.01, 0.02, 0.03, 0.05]

# Create subplot grid for mean reversion strategy plots
fig, axes = plt.subplots(4, 4, figsize=(20, 16))
fig.suptitle('Mean Reversion Strategy - Parameter Exploration', fontsize=16)

# Loop over different parameters
for i, window in enumerate(windows):
    for j, threshold in enumerate(thresholds):
        
        # Apply mean reversion strategy with current parameters
        test_data = strategies.mean_reversion_strategy(data.copy(), window=window, threshold=threshold, ticker=ticker)
        
        # Simulate portfolio (same as before)
        test_data = utils.simulate_portfolio(test_data, f"Mean Reversion (W={window}, T={threshold})", ticker=ticker)
        
        # Plot strategy in subplot
        ax = axes[i, j]
        ax.plot(test_data.index, test_data[f'Close_{ticker}'], label=f'{ticker} Price', linewidth=1, color='gray')
        ax.plot(test_data.index, test_data['RollingMean'], label='Rolling Mean', linewidth=1, color='blue')
        
        # Add threshold bands
        upper_band = test_data['RollingMean'] * (1 + threshold)
        lower_band = test_data['RollingMean'] * (1 - threshold)
        ax.fill_between(test_data.index, upper_band, lower_band, alpha=0.3, color='red', label='Threshold Bands')
        ax.plot(test_data.index, upper_band, linewidth=0.8, color='red', alpha=0.7)
        ax.plot(test_data.index, lower_band, linewidth=0.8, color='red', alpha=0.7)
        
        # Mark buy/sell signals
        buy_signals = test_data[test_data['Position'] == 1]
        ax.scatter(buy_signals.index, buy_signals[f'Close_{ticker}'], marker='^', color='green', label='Buy', s=50, alpha=0.7)
        sell_signals = test_data[test_data['Position'] == -1]
        ax.scatter(sell_signals.index, sell_signals[f'Close_{ticker}'], marker='v', color='red', label='Sell', s=50, alpha=0.7)
        
        ax.set_title(f'W={window}, T={threshold}')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Create subplot grid for mean reversion portfolio plots
fig, axes = plt.subplots(4, 4, figsize=(20, 16))
fig.suptitle('Mean Reversion Strategy - Portfolio Evolution', fontsize=16)

# Loop over different parameters for portfolio plots
for i, window in enumerate(windows):
    for j, threshold in enumerate(thresholds):
        # Apply mean reversion strategy with current parameters
        test_data = strategies.mean_reversion_strategy(data.copy(), window=window, threshold=threshold, ticker=ticker)
        
        # Simulate portfolio
        test_data = utils.simulate_portfolio(test_data, f"Mean Reversion (W={window}, T={threshold})", ticker=ticker)
        
        # Plot portfolio evolution in subplot
        ax = axes[i, j]
        ax.plot(test_data.index, test_data['PortfolioValue'], label='Portfolio Value', linewidth=1.5, color='blue')
        
        # Mark buy/sell signals on portfolio
        buy_signals = test_data[test_data['Position'] == 1]
        ax.scatter(buy_signals.index, buy_signals['PortfolioValue'], marker='^', color='green', label='Buy', s=50, alpha=0.7)
        sell_signals = test_data[test_data['Position'] == -1]
        ax.scatter(sell_signals.index, sell_signals['PortfolioValue'], marker='v', color='red', label='Sell', s=50, alpha=0.7)
        
        ax.set_title(f'W={window}, T={threshold}')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Parameter exploration for momentum strateg
# Define parameter ranges to test for momentum
momentum_windows = [10, 20, 30, 50]

# Create subplot grid for momentum strategy plots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Momentum Strategy - Parameter Exploration', fontsize=16)

# Loop over different parameters for momentum
for i, window in enumerate(momentum_windows):
    
    # Apply momentum strategy with current parameters
    test_data = strategies.simple_momentum_strategy(data.copy(), window=window, ticker=ticker)
    
    # Simulate portfolio (same as before)
    test_data = utils.simulate_portfolio(test_data, f"Momentum (W={window})", ticker=ticker)
    
    # Plot strategy in subplot
    row = i // 2
    col = i % 2
    ax = axes[row, col]
    
    ax.plot(test_data.index, test_data[f'Close_{ticker}'], label=f'{ticker} Price', linewidth=1, color='gray')
    ax.plot(test_data.index, test_data['RollingMean'], label='Rolling Mean', linewidth=1, color='blue')
    
    # Mark buy/sell signals
    buy_signals = test_data[test_data['Position'] == 1]
    ax.scatter(buy_signals.index, buy_signals[f'Close_{ticker}'], marker='^', color='green', label='Buy', s=50, alpha=0.7)
    sell_signals = test_data[test_data['Position'] == -1]
    ax.scatter(sell_signals.index, sell_signals[f'Close_{ticker}'], marker='v', color='red', label='Sell', s=50, alpha=0.7)
    
    ax.set_title(f'Window={window}')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Create subplot grid for momentum portfolio plots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Momentum Strategy - Portfolio Evolution', fontsize=16)

# Loop over different parameters for momentum portfolio plots
for i, window in enumerate(momentum_windows):
    # Apply momentum strategy with current parameters
    test_data = strategies.simple_momentum_strategy(data.copy(), window=window, ticker=ticker)
    
    # Simulate portfolio
    test_data = utils.simulate_portfolio(test_data, f"Momentum (W={window})", ticker=ticker)
    
    # Plot portfolio evolution in subplot
    row = i // 2
    col = i % 2
    ax = axes[row, col]
    
    ax.plot(test_data.index, test_data['PortfolioValue'], label='Portfolio Value', linewidth=1.5, color='blue')
    
    # Mark buy/sell signals on portfolio
    buy_signals = test_data[test_data['Position'] == 1]
    ax.scatter(buy_signals.index, buy_signals['PortfolioValue'], marker='^', color='green', label='Buy', s=50, alpha=0.7)
    sell_signals = test_data[test_data['Position'] == -1]
    ax.scatter(sell_signals.index, sell_signals['PortfolioValue'], marker='v', color='red', label='Sell', s=50, alpha=0.7)
    
    ax.set_title(f'Window={window}')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# The parameter exploration above shows all the combinations we need
# No need for individual plots since we've covered everything in the subplot grids