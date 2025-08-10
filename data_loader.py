import yfinance as yf
import pandas as pd
import sys
import ai_utils
from datetime import datetime, timedelta

def parse_ticker_argument():
    """Parse command line arguments for ticker symbol."""
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
        print(f"Using ticker: {ticker}")
        return ticker
    else:
        ticker = 'BTC-USD'
        print("WARNING: No ticker specified. Using default BTC-USD. Usage: python main.py <TICKER>")
        return ticker

def download_ticker_data(ticker, start_date=None, end_date=None):
    """
    Download historical data for a given ticker with error handling.
    
    Parameters:
    - ticker: Stock ticker symbol
    - start_date: Start date for historical data (default: 1 year ago)
    - end_date: End date for historical data (default: today)
    
    Returns:
    - pd.DataFrame: Historical price data
    """
    # Set default dates: 1 year of data up to today
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    print(f"Downloading data for {ticker}...")
    
    try:
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
        
        if data.empty or len(data) == 0:
            handle_download_failure(ticker)
            sys.exit(1)
            
        print(f"Successfully downloaded {len(data)} days of data for {ticker} ({start_date} to {end_date})")
        return data
        
    except Exception as e:
        print(f"ERROR: Failed to download data for ticker '{ticker}': {e}")
        handle_download_failure(ticker)
        sys.exit(1)

def handle_download_failure(ticker):
    """Handle failed ticker download with AI-powered suggestions."""
    print(f"ERROR: Failed to download data for ticker '{ticker}'")
    
    # Generate AI-powered intelligent suggestions
    suggestions = ai_utils.get_ai_ticker_suggestions(ticker)
    
    if suggestions:
        print(f"\nDid you mean one of these?")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"  {i}. {suggestion}")
        print(f"\nTry: python main.py {suggestions[0]}")
    else:
        print("\nPossible reasons:")
        print("  - Ticker doesn't exist or is delisted")
        print("  - Wrong ticker format")
        print("  - Network/API issues")
        
    print("\nCommon formats:")
    print("  US stocks: AAPL, TSLA, MSFT")
    print("  Crypto: BTC-USD, ETH-USD")
    print("  European: TICKER.L (London), TICKER.DE (Germany)")

def normalize_data_columns(data, ticker):
    """
    Normalize data columns to ensure consistent column naming.
    
    Parameters:
    - data: DataFrame with financial data
    - ticker: Ticker symbol for column naming
    
    Returns:
    - pd.DataFrame: Data with normalized columns
    """
    # Normalize columns once: flatten first if MultiIndex, then ensure Close_{ticker} exists
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] if col[1] == '' else f"{col[0]}_{col[1]}" for col in data.columns]

    if f'Close_{ticker}' not in data.columns:
        if 'Close' in data.columns:
            # 'Close' is a Series after flatten or a simple column; ensure we take a Series
            data[f'Close_{ticker}'] = data['Close']
        elif f'{ticker}_Close' in data.columns:
            data[f'Close_{ticker}'] = data[f'{ticker}_Close']
    
    return data

def load_and_prepare_data(ticker=None, start_date=None, end_date=None):
    """
    Main function to load and prepare ticker data.
    
    Parameters:
    - ticker: Optional ticker symbol (if None, will parse from command line)
    - start_date: Start date for historical data (default: 1 year ago)
    - end_date: End date for historical data (default: today)
    
    Returns:
    - tuple: (ticker, normalized_data)
    """
    if ticker is None:
        ticker = parse_ticker_argument()
    
    data = download_ticker_data(ticker, start_date, end_date)
    data = normalize_data_columns(data, ticker)
    
    return ticker, data