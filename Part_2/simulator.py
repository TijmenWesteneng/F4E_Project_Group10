import numpy as np
import pandas as pd
import yfinance as yf

import os.path
import datetime
import time
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

        # Amount of dataframe entries given to bots in first cycle
        self.history = 10

        self.stock_data = self.get_stock_data()
        print(self.stock_data)

    def simulate(self):
        for i in range(self.history, len(self.stock_data.index)):
            self.sim_cycle(self.stock_data.iloc[:i])

    def sim_cycle(self, stock_data):
        print(stock_data)

    # TODO: Make get stock data able to get more data than the max of yfinance by looping
    def get_stock_data(self):
        """Gets stock data from yahoo finance and puts it in a dataframe"""
        tickers = get_sp500_tickers(self.stock_amount)

        filename = str(str(self.stock_amount) + "-" + str(time.mktime(self.start_date.timetuple())) + "-" +
                       str(time.mktime(self.end_date.timetuple())) + ".csv")

        if not self.load_df(filename).empty:
            return self.load_df(filename)
        else:
            stock_data = self.read_price_data(tickers, self.start_date, self.end_date, self.interval)
            self.save_df(stock_data, filename)
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

    def save_df(self, df: pd.DataFrame, filename):
        df.to_csv(filename)

    def load_df(self, filename):
        if not os.path.isfile(filename):
            return pd.DataFrame

        return pd.read_csv(filename)


sim = Simulator("bot_array", 10, datetime.date.today() - relativedelta(days=60), datetime.date.today(), '1h')
sim.simulate()
