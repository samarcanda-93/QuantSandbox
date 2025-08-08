# Simple Momentum Strategy: Calculate the rolling mean of the closing price and use it to generate buy and sell signals.
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def simple_momentum_strategy(data, window=20, ticker='TSLA'):
    # Create a copy to avoid modifying the original data
    data = data.copy()
    
    # Handle MultiIndex columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        # Flatten the column names
        data.columns = [col[0] if col[1] == '' else f"{col[0]}_{col[1]}" for col in data.columns]

    # Ensure standardized close column exists
    if f'Close_{ticker}' not in data.columns:
        if 'Close' in data.columns:
            data[f'Close_{ticker}'] = data['Close']
        elif f'{ticker}_Close' in data.columns:
            data[f'Close_{ticker}'] = data[f'{ticker}_Close']

    close_series = data[f'Close_{ticker}'] if isinstance(data[f'Close_{ticker}'], pd.Series) else data[f'Close_{ticker}'].squeeze()

    # compute shifted rolling mean
    data['RollingMean'] = close_series.rolling(window=window).mean().shift(1) 
    # drop all rows where RollingMean is NaN.
    data = data.dropna(subset=['RollingMean'])
    data['Signal']   = (data[f'Close_{ticker}'] > data['RollingMean']).astype(int)
    data['Position'] = data['Signal'].diff()

    return data


def mean_reversion_strategy(data, window=20, threshold=0.02, ticker='TSLA'):
    # Create a copy to avoid modifying the original data
    data = data.copy()
    
    # Handle MultiIndex columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        # Flatten the column names
        data.columns = [col[0] if col[1] == '' else f"{col[0]}_{col[1]}" for col in data.columns]

    # Ensure standardized close column exists
    if f'Close_{ticker}' not in data.columns:
        if 'Close' in data.columns:
            data[f'Close_{ticker}'] = data['Close']
        elif f'{ticker}_Close' in data.columns:
            data[f'Close_{ticker}'] = data[f'{ticker}_Close']

    close_series = data[f'Close_{ticker}'] if isinstance(data[f'Close_{ticker}'], pd.Series) else data[f'Close_{ticker}'].squeeze()
    
    # Pure mean-reversion strategy bands
    data['RollingMean'] = close_series.rolling(window=window).mean().shift(1)
    lower_band =  data['RollingMean'] * (1 - threshold)
    upper_band =  data['RollingMean'] * (1 + threshold)

    # Signals and positions
    data['Signal'] = pd.Series(0, index=data.index, dtype=int)
    data.loc[data[f'Close_{ticker}'] < lower_band, 'Signal'] = 1
    data.loc[data[f'Close_{ticker}'] > upper_band, 'Signal'] = -1
    data['Position'] = data['Signal'].diff()
    
    return data