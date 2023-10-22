import numpy as np
import yfinance as yf
import datetime
from dateutil.relativedelta import relativedelta

from sp500 import get_sp500_tickers


class Simulator:

    def __init__(self, bot_array, stock_amount: int, start_date, end_date, interval):
        """
        Creates a simulator object using specified parameters
        :param bot_array: array with bot objects used in simulation
        :param stock_amount: integer amount of stocks to simulate on (from S&P500)
        :param start_date: date to start simulation from (historical data)
        :param end_date: date to stop simulation (e.g. today)
        :param interval: interval between simulation data points
        """
        self.bot_array = bot_array
        self.stock_amount = stock_amount
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval

        self.stock_data = self.get_stock_data()
        print(self.stock_data)

    def get_stock_data(self):
        """Gets stock data from yahoo finance and puts it a dataframe"""
        tickers = get_sp500_tickers(self.stock_amount)

        stock_data = self.read_price_data(tickers, self.start_date, self.end_date, self.interval)
        return stock_data

    def read_price_data(self, stock_symbol, start_date, end_date, interval):
        """Imports price data from Yahoo Finance"""
        try:
            stock_data = yf.download(stock_symbol, start_date, end_date, interval=interval)
        except:
            return None

        prices = stock_data.loc[:, "Adj Close"]
        prices = prices.ffill()

        return prices


Simulator("bot_array", 1, datetime.date.today() - relativedelta(years=1), datetime.date.today(), '1mo')
