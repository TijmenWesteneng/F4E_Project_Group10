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

    def get_stock_data(self):
        """Gets stock data from yahoo finance and puts it in a dataframe"""
        tickers = get_sp500_tickers(self.stock_amount)

        filename = str(str(self.stock_amount) + "_" + self.interval + "_" +
                       self.start_date.strftime("%m-%d-%Y") + "_" +
                       self.end_date.strftime("%m-%d-%Y") + ".csv")

        if not self.load_df(filename).empty:
            return self.load_df(filename)
        else:
            stock_data = self.download_stock_data_loop(tickers, self.start_date, self.end_date, self.interval)
            self.save_df(stock_data, filename)
            return stock_data

    def download_stock_data_loop(self, tickers, start_date, end_date, interval):
        """Downloads stock data from yahoo finance using loops if more than max data_amount per request is needed"""
        df_list = list()
        timespan = end_date - start_date
        days = timespan.days

        if interval == "1m":
            if days <= 7:
                return self.read_price_data(tickers, start_date, end_date, interval)
            else:
                current_start_date = start_date
                current_end_date = current_start_date + relativedelta(days=7)
                while current_end_date < end_date:
                    df = self.read_price_data(tickers, current_start_date, current_end_date, interval)
                    df_list.append(df)
                    current_start_date = current_end_date
                    current_end_date = current_start_date + relativedelta(days=7)

                if current_start_date != end_date:
                    df = self.read_price_data(tickers, current_start_date, end_date, interval)
                    df_list.append(df)

        elif interval == "2m" or interval == "5m" or interval == "15m" or interval == "30m" or interval == "60m" \
                or interval == "90m" or interval == "1h":
            if days <= 60:
                return self.read_price_data(tickers, start_date, end_date, interval)
            else:
                current_start_date = start_date
                current_end_date = current_start_date + relativedelta(days=60)
                while current_end_date < end_date:
                    df = self.read_price_data(tickers, current_start_date, current_end_date, interval)
                    df_list.append(df)
                    current_start_date = current_end_date
                    current_end_date = current_start_date + relativedelta(days=60)

                if current_start_date != end_date:
                    df = self.read_price_data(tickers, current_start_date, end_date, interval)
                    df_list.append(df)

        else:
            return self.read_price_data(tickers, start_date, end_date, interval)

        return pd.concat(df_list)

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


sim = Simulator("bot_arr", 10, datetime.date(2023, 10, 23) - relativedelta(days=121), datetime.date(2023, 10, 23), '1h')
sim.simulate()
