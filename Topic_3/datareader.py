import yfinance as yf
import pandas as pd


def read_price_data(stock_symbol, start_date, end_date, interval):
    """Import price data from Yahoo Finance"""
    try:
        stock_data = yf.download(stock_symbol, start_date, end_date, interval=interval)
    except:
        return None

    prices = stock_data.loc[:, "Adj Close"]
    prices = prices.ffill()
    prices = prices.pct_change()*100
    prices = prices.dropna()

    ticker = yf.Ticker(stock_symbol)
    company_name = ticker.info['longName']

    return company_name, prices.values

