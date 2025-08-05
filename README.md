# QuantSandbox

A Python-based quantitative trading sandbox for backtesting and analyzing algorithmic trading strategies on cryptocurrency and financial data.

## Features

- **Momentum Strategy**: Trend-following strategy using rolling mean crossovers
- **Mean Reversion Strategy**: Counter-trend strategy using statistical bands
- **Parameter Exploration**: Grid search functionality for strategy optimization
- **Portfolio Simulation**: Simple backtesting with position tracking
- **Visualization**: Comprehensive plotting of strategy performance and signals

## Strategies Implemented

### 1. Simple Momentum Strategy
- Uses rolling mean as trend indicator
- Buy when price > rolling mean, sell when price < rolling mean
- Configurable window parameter (default: 20 periods)
- Includes look-ahead bias prevention with `.shift(1)`

### 2. Mean Reversion Strategy
- Uses statistical bands around rolling mean
- Buy when price drops below lower band (mean - threshold%)
- Sell when price rises above upper band (mean + threshold%)
- Configurable window and threshold parameters

## Installation

1. Clone or download this repository
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main sandbox script:
```bash
python sandbox.py
```

This will:
- Download BTC-USD data from Yahoo Finance
- Run both strategies with parameter exploration
- Generate visualization plots showing:
  - Strategy signals and price action
  - Portfolio value evolution
  - Parameter sensitivity analysis

## File Structure

- `sandbox.py` - Main execution script with parameter exploration
- `strategies.py` - Strategy implementations (momentum and mean reversion)
- `utils.py` - Portfolio simulation utilities
- `requirements.txt` - Python dependencies

## Configuration

Key parameters you can modify in `sandbox.py`:

- **Ticker**: Change `ticker = 'BTC-USD'` to any Yahoo Finance symbol
- **Date Range**: Modify `start` and `end` parameters in `yf.download()`
- **Strategy Parameters**: 
  - Momentum windows: `[10, 20, 30, 50]`
  - Mean reversion windows: `[10, 20, 30, 50]`
  - Mean reversion thresholds: `[0.01, 0.02, 0.03, 0.05]`

## Output

The script generates multiple visualization plots:
1. Mean reversion strategy signals with parameter grid (4x4 subplots)
2. Mean reversion portfolio evolution (4x4 subplots)  
3. Momentum strategy signals with different windows (2x2 subplots)
4. Momentum portfolio evolution (2x2 subplots)

## Notes

- Strategies include proper look-ahead bias prevention
- Portfolio simulation uses simple position sizing (all-in/all-out)
- No transaction costs or slippage modeling
- Results are for educational/research purposes only

## Future Enhancements

- Add more sophisticated risk management
- Implement additional technical indicators
- Include performance metrics (Sharpe ratio, max drawdown, etc.)
- Add backtesting statistics and reporting
- Support for multiple assets and portfolio optimization