import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to simulate portfolio
def simulate_portfolio(data, strategy_name, ticker='TSLA'):
    
    initial_cash = 100
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
        
        # Correct portfolio value calculation
        portfolio_value = cash + (position * price)
        portfolio_values.append(portfolio_value)
    
    data['PortfolioValue'] = portfolio_values
    return data