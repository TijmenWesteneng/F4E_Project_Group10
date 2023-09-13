# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 11:22:11 2023

@author: Joost
@author Tijmen
"""


import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
from dateutil.relativedelta import relativedelta
from capm_tool import capm_calculator


def read_price_data(stock_symbol, start_date, end_date, interval):
    """Import price data from Yahoo Finance"""
    try:
        stock_data = yf.download(stock_symbol, start_date, end_date, interval=interval)
    except:
        return None

    prices = stock_data.loc[:, "Adj Close"]
    prices = prices.ffill()

    return prices


def get_date_list(stock_symbol, start_date, end_date, interval):
    """Generate list of trading dates"""
    stock_data = yf.download(stock_symbol, start_date, end_date, interval=interval)
    dates = stock_data.index
    
    return dates


index_symbol = "^GSPC" # Index symbol (by default "^GSPC" for the S&P500 index)
stock_symbol = "MSFT" # Stock symbol

# Generate list of trading days
start_date = datetime.date.today() - relativedelta(years=5)
end_date = datetime.date.today()
interval = '1mo' # Date interval, by default daily ('1d')
date_list = get_date_list(index_symbol, start_date, end_date, interval=interval)

# Generate empty dataframe
column_header_index = "Index price ({})".format(index_symbol)
column_header_stock = "Stock price ({})".format(stock_symbol)
df = pd.DataFrame(
        columns=[column_header_index, column_header_stock], index=date_list
    )

# Sort dataframe based on date
df = df.sort_index(ascending=False)  

# Import price series into dataframe
try:
    price_series = read_price_data(index_symbol, start_date, end_date, interval=interval)
    df[column_header_index] = price_series
    
    price_series = read_price_data(stock_symbol, start_date, end_date, interval=interval)
    df[column_header_stock] = price_series  
except:
    print('Import failed')

capm_calculator(df)

# Print dataframe
df.plot()
plt.show()

# Example of plotting a scatterplot
""" 
x = [8, 0, 12, 4, 5]
y = [1, 5, 3, -1, 7]
plt.scatter(x, y, marker='o')
plt.xlabel('x-label')
plt.ylabel('y-label')
plt.show()
"""
