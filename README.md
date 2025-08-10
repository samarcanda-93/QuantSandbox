# QuantSandbox

A comprehensive Python framework for backtesting, optimizing, and analyzing quantitative trading strategies with AI-powered insights and PDF reporting. 

## Features

- **Momentum Strategy**: Trend-following strategy using rolling mean crossovers
- **Mean Reversion Strategy**: Counter-trend strategy using statistical bands
- **Parameter Exploration**: Grid search functionality for strategy optimization
- **Portfolio Simulation**: Simple backtesting with position tracking
- **Visualization**: Plots now show both **Sharpe** and **Max Drawdown** in titles/legends (including strategy comparisons)
- **PDF Reports**: Basic and Full reports with summaries, charts, risk metrics, and a “Today’s suggestion” line
- **End‑of‑Run Suggestion**: Console and PDF display a concise Buy/Sell/Hold suggestion based on the best strategy

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

### 2. Portfolio Analysis
- Plots annotate both Sharpe and Max Drawdown across parameter grids and comparison charts
- End‑of‑run “Today’s suggestion” is printed to the console and included in PDF summaries
- PDF basic summary and full executive summary now include a “Today’s suggestion” line
- AI-generated analyis of the strategy.

## Installation

### Prerequisites

You'll need Python 3.8 or higher installed on your system.

### 1. Clone or download this repository

```bash
git clone <repository-url>
cd QuantSandbox
```

### 2. Install dependencies

#### Windows

```cmd
# Create and activate virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Linux (Debian/Ubuntu)

```bash
# Install Python and pip if not already installed
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Linux (RedHat/CentOS/Fedora)

```bash
# Install Python and pip if not already installed (CentOS/RHEL 8+)
sudo dnf install python3 python3-pip python3-venv

# For older CentOS/RHEL 7
# sudo yum install python3 python3-pip

# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. API Setup

This project now supports AI-powered features using Gemini and Hugging Face APIs.

#### Google Gemini API

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set the environment variable:

**Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your_api_key_here"
```

**Windows (System Environment Variables):**
1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables" or "System variables", click "New"
5. Variable name: `GOOGLE_API_KEY`
6. Variable value: `your_api_key_here`

**Linux:**
```bash
export GOOGLE_API_KEY=your_api_key_here
```

**Linux (Persistent - add to ~/.bashrc or ~/.profile):**
```bash
echo 'export GOOGLE_API_KEY=your_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

#### Hugging Face API

1. Visit [Hugging Face](https://huggingface.co/settings/tokens)
2. Create a new access token
3. Set the environment variable:

**Windows (Command Prompt):**
```cmd
set HUGGINGFACE_API_KEY=your_token_here
```

**Windows (PowerShell):**
```powershell
$env:HUGGINGFACE_API_KEY="your_token_here"
```

**Windows (System Environment Variables):**
1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables" or "System variables", click "New"
5. Variable name: `HUGGINGFACE_API_KEY`
6. Variable value: `your_token_here`

**Linux:**
```bash
export HUGGINGFACE_API_KEY=your_token_here
```

**Linux (Persistent - add to ~/.bashrc or ~/.profile):**
```bash
echo 'export HUGGINGFACE_API_KEY=your_token_here' >> ~/.bashrc
source ~/.bashrc
```

For persistent environment variables, add them to your system's environment configuration or shell profile.

### 4. API Testing and Debugging

The project includes several debugging scripts to test API connectivity:

#### Google Gemini API Testing
```bash
python tests/test_gemini_api.py
```
Tests the Gemini API connection directly and verifies your API key is working.

#### Hugging Face API Testing
```bash
python tests/test_huggingface_api.py
```
Tests Hugging Face API connectivity and ticker suggestion functionality.

#### Hugging Face Error Testing
```bash
python tests/test_huggingface_errors.py
```
Tests various error scenarios for the Hugging Face API to ensure robust error handling.

#### AI Integration Testing
```bash
python tests/test_ai_integration.py INVALID_TICKER
```
Tests the integrated AI ticker suggestion system with a specific ticker.

These debugging tools are helpful for:
- Verifying API keys are correctly configured
- Testing API connectivity and response times
- Debugging ticker suggestion accuracy
- Understanding error handling behavior

## Usage

### Basic Usage

Run the main application:
```bash
python main.py
```

### Custom Ticker

You can specify any ticker symbol as a command line argument:
```bash
python main.py AAPL
python main.py TSLA
python main.py ETH-USD
python main.py MSFT
```

The main.py script offers two analysis modes:
1. **Basic comparison** - Quick Sharpe ratio comparison of strategies
2. **Full exploration** - Complete parameter optimization with visualizations

The script will:
- Download historical data for the specified ticker from Yahoo Finance
- Run both strategies with parameter exploration
- Generate visualization plots showing:
  - Strategy signals and price action
  - Portfolio value evolution
  - Parameter sensitivity analysis
- If the ticker fails to download, AI-powered suggestions will be provided (if APIs are configured)
- Print a “Today’s suggestion” line

### “Today’s suggestion” logic

- The suggestion is derived from the latest row of the selected strategy’s output:
  - **Action**: based on the latest `Position` change (+1=Buy, −1=Sell, 0=Hold)
  - **State**: based on the latest `Signal` (>0=Long, else Flat)
- Strategy selection:
  - In Basic mode: whichever strategy (Momentum vs Mean Reversion) has the higher Sharpe
  - In Full mode: higher Sharpe between the best‑parameter Mean Reversion and Momentum runs
- Context shown: date and last price for the asset
- Note: uses the latest available bar from Yahoo Finance; if today’s bar isn’t updated yet, it reflects the most recent close

### PDF reports

- You’ll be prompted to generate a PDF at the end of runs
- Reports include: summary/executive summary, portfolio charts, risk metrics, parameter heatmaps and comparisons, AI-generated market analysis, and “Today’s suggestion”
- Filenames follow patterns like `strategy_report_<TICKER>_<timestamp>.pdf` or `full_analysis_report_<TICKER>_<timestamp>.pdf`
- Each suggestion is accompanied by the disclaimer: “This is not financial advice.”

## File Structure

### Core Application
- `main.py` - Main execution script with interactive interface and modular architecture

### Modular Components  
- `data_loader.py` - Data download, validation, and preprocessing
- `parameter_explorer.py` - Strategy parameter optimization and testing
- `plotting.py` - Modular visualization and charting functions
- `strategies.py` - Strategy implementations (momentum and mean reversion)
- `finance_utils.py` - Portfolio simulation, risk metrics, and financial calculations
-    - Includes Sharpe (with live risk‑free rate fallback) and Max Drawdown; provides the `latest_trade_recommendation` helper
- `ai_utils.py` - AI-powered ticker suggestions and API integrations

### Configuration & Testing
- `requirements.txt` - Python dependencies
- `tests/` - API testing and debugging scripts
  - `test_gemini_api.py` - Google Gemini API testing
  - `test_huggingface_api.py` - Hugging Face API testing
  - `test_huggingface_errors.py` - Hugging Face error scenario testing
  - `test_ai_integration.py` - Integrated AI ticker suggestion testing

## Configuration

The application provides two analysis modes:

### Basic Comparison Mode
- **Interactive Parameter Selection**: Choose custom window sizes and thresholds
- **Fast Results**: Quick strategy comparison with Sharpe ratios
- **Optional Visualization**: Simple comparison chart

### Full Exploration Mode  
- **Comprehensive Grid Search**: Tests multiple parameter combinations
- **Advanced Visualizations**: Strategy signals and portfolio evolution plots
- **Best Parameter Discovery**: Automatically finds optimal configurations

**Default Parameter Ranges:**
- **Momentum Strategy**: Windows from 5 to 200 periods
- **Mean Reversion Strategy**: Windows from 5 to 200 periods, thresholds from 0.1% to 10%

## Output

The script generates multiple visualization plots:
1. Mean reversion strategy signals with parameter grid (4x4 subplots)
2. Mean reversion portfolio evolution (4x4 subplots)  
3. Momentum strategy signals with different windows (2x2 subplots)
4. Momentum portfolio evolution (2x2 subplots)

## Trading Model & Assumptions

### Portfolio Simulation Details
The backtesting system uses a simplified trading model:

- **Initial Capital**: $100 starting investment
- **Position Sizing**: All-in/all-out approach
  - **Buy Signal**: Invest entire available cash (100% allocation)
  - **Sell Signal**: Liquidate entire position (convert to cash)
  - **Hold Signal**: Maintain current position (no action)

### Trading Logic
1. **Mean Reversion Strategy**: 
   - Buy when price falls below (moving average - threshold%)
   - Sell when price rises above (moving average + threshold%)
2. **Momentum Strategy**:
   - Buy when price crosses above moving average
   - Sell when price crosses below moving average

### Important Limitations

**⚠️ Simplifications in Current Model:**
- **No Transaction Costs**: Assumes zero brokerage fees, commissions, or spreads
- **No Slippage**: Assumes perfect execution at exact signal prices
- **No Market Impact**: Assumes orders don't affect market prices
- **Binary Position Sizing**: Only 0% or 100% allocation (no partial positions)
- **Instant Execution**: Assumes immediate fills without delays
- **Perfect Liquidity**: Assumes ability to buy/sell any amount instantly
- **No Margin Requirements**: No borrowing costs or margin calls
- **Tax Ignorance**: No consideration of capital gains taxes or wash sale rules

**📊 Real-World Impact:**
- **Transaction costs** typically range from 0.01% to 0.5% per trade
- **Bid-ask spreads** can reduce returns, especially for frequent trading
- **Market gaps** may cause execution at worse prices than signals indicate
- **Position sizing** in practice should consider risk management and diversification
- **Regulatory constraints** like pattern day trading rules may apply

**🎯 Educational Purpose:**
This simplified model is designed for:
- Understanding strategy logic and parameter sensitivity
- Comparing relative performance between different approaches
- Learning quantitative finance concepts without complexity

**Real trading would require:**
- Proper position sizing and risk management
- Transaction cost modeling
- Slippage and market impact considerations
- Regulatory compliance
- Professional risk management tools

## Notes

- Strategies include proper look-ahead bias prevention
- Results are for educational/research purposes only
- Suggestions shown in console and PDFs are informational and **not financial advice**

## Future Enhancements
- Add more sophisticated risk management
- Implement additional indicators
- Add additional performance metrics (Sortino, Calmar, hit rate, exposure, etc.)
- Support for multiple assets and portfolio optimization
- **Custom Ticker Recognition Model**: Train a specialized machine learning model for improved ticker suggestion accuracy
  - Fine-tune language models (BERT/DistilBERT) on company name → ticker mappings
  - Create embedding-based similarity matching using financial datasets
  - Incorporate multi-modal features (sector, market cap, geographic data)
  - Train on comprehensive datasets from SEC EDGAR, exchange listings, and user interaction logs
  - Implement incremental learning to continuously improve from real usage patterns
  - Handle regional exchanges and edge cases better than current general-purpose AI APIs