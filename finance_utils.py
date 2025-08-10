import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def simulate_portfolio(data, strategy_name, ticker='TSLA', initial_cash=100):
    """
    Simulate portfolio performance based on trading signals.
    
    Parameters:
    - data: DataFrame with 'Position' column containing trading signals
    - strategy_name: String name of the strategy (for reference)
    - ticker: Stock ticker symbol (default 'TSLA')
    - initial_cash: Starting cash amount (default 100)
    
    Returns:
    - DataFrame with added 'PortfolioValue' column
    """
    data = data.copy()

    # Ensure standardized close column exists
    if f'Close_{ticker}' not in data.columns:
        if 'Close' in data.columns:
            data[f'Close_{ticker}'] = data['Close']
        elif f'{ticker}_Close' in data.columns:
            data[f'Close_{ticker}'] = data[f'{ticker}_Close']

    cash = initial_cash
    position = 0
    in_market = False
    portfolio_values = []
    
    for idx, row in data.iterrows():
        price = row[f'Close_{ticker}']
        signal = row['Position']
        
        if not in_market:
            if signal == 1:
                position = cash / price
                cash = 0
                in_market = True
        else:
            if signal == 1:
                pass  # Already in market
            elif signal == -1:
                cash = position * price
                position = 0
                in_market = False
        
        portfolio_value = cash + (position * price)
        portfolio_values.append(portfolio_value)
    
    data['PortfolioValue'] = portfolio_values
    return data

def get_current_risk_free_rate():
    """
    Fetch current 10-year US Treasury yield as risk-free rate.
    Tries multiple sources with fallback hierarchy.
    
    Returns:
    - tuple: (rate, source_description)
    """
    
    # Method 1: Try yfinance (^TNX - 10 Year Treasury)
    try:
        treasury = yf.download('^TNX', period='5d', progress=False, auto_adjust=False)
        if not treasury.empty and len(treasury) > 0:
            # Handle MultiIndex columns
            if isinstance(treasury.columns, pd.MultiIndex):
                close_col = ('Close', '^TNX')
            else:
                close_col = 'Close'
            
            current_yield = treasury[close_col].iloc[-1] / 100
            if not pd.isna(current_yield) and current_yield > 0:
                return current_yield, "Yahoo Finance (^TNX - 10Y Treasury)"
    except Exception as e:
        print(f"yfinance fetch failed: {e}")
    
    # Method 2: Try web search for current rate
    try:
        import requests
        import re
        
        # Try a few financial websites
        urls = [
            ("https://www.marketwatch.com/investing/bond/tmubmusd10y", r'(\d+\.\d+)%'),
            ("https://finance.yahoo.com/quote/%5ETNX/", r'(\d+\.\d+)')
        ]
        
        for url, pattern in urls:
            try:
                response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        rate = float(matches[0]) / 100
                        if 0.001 < rate < 0.20:  # Sanity check: 0.1% to 20%
                            return rate, f"Web scraping ({url.split('/')[2]})"
            except:
                continue
    except:
        pass
    
    # Method 3: Try FRED API alternative (simplified)
    try:
        # Alternative yfinance symbols
        for symbol in ['^TNX', 'DGS10']:
            try:
                data = yf.download(symbol, period='1d', progress=False)
                if not data.empty:
                    rate = data['Close'].iloc[-1] / 100 if symbol == '^TNX' else data['Close'].iloc[-1] / 100
                    if not pd.isna(rate) and rate > 0:
                        return rate, f"Yahoo Finance ({symbol})"
            except:
                continue
    except:
        pass
    
    # Final fallback
    return 0.02, "Default fallback (yfinance and web sources failed)"

def calculate_sharpe_ratio(data, risk_free_rate=None, print_rate_info=False):
    """
    Calculate Sharpe ratio for portfolio performance.
    
    Parameters:
    - data: DataFrame with 'PortfolioValue' column
    - risk_free_rate: Annual risk-free rate (if None, fetches current 10Y Treasury)
    - print_rate_info: Whether to print risk-free rate source info
    
    Returns:
    - sharpe_ratio: Risk-adjusted return metric
    """
    if 'PortfolioValue' not in data.columns:
        return None
    
    # Get current risk-free rate if not provided
    if risk_free_rate is None:
        risk_free_rate, source = get_current_risk_free_rate()
        if print_rate_info:
            print(f"📊 Risk-free rate: {risk_free_rate:.3%} (Source: {source})")
    
    # Calculate daily returns
    portfolio_values = data['PortfolioValue']
    daily_returns = portfolio_values.pct_change().dropna()
    
    if len(daily_returns) == 0:
        return None
    
    # Annualize returns and volatility (assuming daily data)
    annual_return = daily_returns.mean() * 252
    annual_volatility = daily_returns.std() * np.sqrt(252)
    
    # Calculate Sharpe ratio
    if annual_volatility == 0:
        return None
    
    excess_return = annual_return - risk_free_rate
    sharpe_ratio = excess_return / annual_volatility
    
    return sharpe_ratio