# Simple Momentum Strategy: Calculate the rolling mean of the closing price and use it to generate buy and sell signals.
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def simple_momentum_strategy(data, window=20, ticker='TSLA'):
    # Create a copy to avoid modifying the original data
    data = data.copy()
    
    # Handle MultiIndex columns from yfinance
    print('Type of data.columns:', type(data.columns))
    if isinstance(data.columns, pd.MultiIndex):
        # Flatten the column names
        data.columns = [col[0] if col[1] == '' else f"{col[0]}_{col[1]}" for col in data.columns]
    # compute shifted rolling mean
    data['RollingMean'] = data[f'Close_{ticker}'].rolling(window=window).mean().shift(1) 
    # shift(1) is added to avoid look-ahead bias.  
    # The rolling mean is calculated over a window of past closing prices (here, the last 20 days). 
    # By default, the rolling mean for a given day includes that day's closing price. 
    # In a real trading scenario, you cannot use today's closing price to make a decision for today — you only have access to past data up to yesterday.
    # drop all rows where RollingMean is NaN.
    data = data.dropna(subset=['RollingMean'])
    data['Signal']   = (data[f'Close_{ticker}'] > data['RollingMean']).astype(int) # 1 if the closing price is greater than the rolling mean, 0 otherwise.
    data['Position'] = data['Signal'].diff() # 1 if the closing price is greater than the rolling mean, -1 if the closing price is less than the rolling mean, 0 otherwise.

    return data


def mean_reversion_strategy(data, window=20, threshold=0.02, ticker='TSLA'):
    # Create a copy to avoid modifying the original data
    data = data.copy()
    
    # Handle MultiIndex columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        # Flatten the column names
        data.columns = [col[0] if col[1] == '' else f"{col[0]}_{col[1]}" for col in data.columns]
    
    # Pure mean-reversion strategy:
    # - Buy when price < MA * (1 - threshold)
    # - Sell when price > MA * (1 + threshold)
    # - Hold (0) otherwise
    
    # compute the N-day moving average
    data['RollingMean'] = data[f'Close_{ticker}'].rolling(window=window).mean().shift(1)
    # shift(1) is added to avoid look-ahead bias
    # define upper/lower bands
    lower_band =  data['RollingMean'] * (1 - threshold)
    upper_band =  data['RollingMean'] * (1 + threshold)
    # initialize signals to 0
    data['Signal'] = pd.Series(0, index=data.index, dtype=int)
    # buy when price dips below lower band
    data['Signal'].loc[data[f'Close_{ticker}'] < lower_band] = 1
    # sell when price rises above upper band
    data['Signal'].loc[data[f'Close_{ticker}'] > upper_band] = -1
    # generate position changes: +1 for buy, -1 for sell, 0 for hold
    data['Position'] = data['Signal'].diff()
    
    return data