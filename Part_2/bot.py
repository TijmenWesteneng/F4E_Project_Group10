import math

import numpy as np
import pandas as pd


class BotTemplate:
    def __init__(self, start_cash, stock_size: int):
        """
        Creates a Bot that makes a trading decision based on the incoming data
        :param start_cash: double of amount of cash that the bot starts with in the beginning
        :param stock_size: integer of the amount of unique stocks the program will feed to the bot
        """
        self.cash = start_cash
        self.stocks = pd.DataFrame
        self.value = self.cash

        # TODO: keep track of selling and buying behavior on each stock
    def initiate(self, name_list: list):
        """
        Fill stock dataframe with the names of the stocks
        :param name_list: list with all names of the stocks
        """
        for name in name_list:
            self.stocks[name] = 0

    def calc_worth(self, hist_data: pd.DataFrame):
        """
        Calculate worth of cash and all stocks combined
        :param hist_data: matrix of a set of historical values for the given stocks
        """
        worth = self.cash

        for i in self.stocks.columns:
            stock_amount = self.stocks[i].iloc[0]
            stock_price = hist_data[i].iloc[-1]
            worth = worth + stock_amount * stock_price


class BotMovingAverage(BotTemplate):
    def __init__(self, start_cash, stock_size: int, window_size: int):
        """
        Creates a specific trading strategy bot
        :param start_cash: double of amount of cash that the bot starts with in the beginning
        :param stock_size: integer of the amount of unique stocks the program will feed to the bot
        :param window_size: variable upon which the bot behaves differently
        """
        super().__init__(start_cash, stock_size)  # Inherit the class BotTemplate
        self.alfa = window_size

    def trade(self, hist_data: pd.DataFrame):
        """
        Makes trading decisions based on the incoming historical data
        :param hist_data: matrix of a set of historical values for the given stocks
        """
        moving_average = self.mov_avg(hist_data)
        # If moving_average failed, just return
        if moving_average == -1:
            return

        # This is temporary trade function
        key = moving_average.columns[0]  # Get key from first column
        current_value = hist_data.loc[len(hist_data.iloc[:, 0]) - 1, key]

        # If the moving average is larger than the current value of the stock
        if moving_average[key] >= current_value:
            # If stock is not bought yet buy
            if self.stocks[key] == 0:
                # Buy
                value = math.floor(self.cash / current_value)
                stock_amount = value * current_value
                self.stocks[key] = self.stocks[key] + stock_amount  # add stock
                self.cash = self.cash - value  # subtract cash

        # If the moving average is smaller than the current value of the stock
        else:
            # If stock is already bought
            if self.stocks[key] != 0:
                # Sell
                value = self.stocks[key] * current_value
                self.stocks[key] = 0
                self.cash = self.cash + value

        # Calculate the total value of the portfolio
        self.calc_worth(hist_data)

    def mov_avg(self, hist_data: pd.DataFrame):
        """
        Calculates the moving average of the hist_data given
        :param hist_data: matrix of a set of historical values for the given stocks
        """

        # Swap hist_data so last date is in first row
        reversed_hist_data = hist_data.apply(lambda col: col[::-1])

        # Check if the amount of data points is enough for this value of alfa
        column_size = len(hist_data.iloc[:, 0])
        if column_size < self.alfa:
            return -1

        # Calculate moving average
        moving_averages = reversed_hist_data.rolling(window=self.alfa).mean()  # Calculate sliding window mov avg
        moving_average = moving_averages.dropna().iloc[0]  # Extract only the first valid row

        return moving_average
