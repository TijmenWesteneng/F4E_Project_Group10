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
        self.cash = start_cash  # Cash available for bot
        self.stocks = dict()  # Amount of stocks the bot has
        self.value = self.cash  # The total value the bot possesses

        self.hist_trade = pd.DataFrame()  # All the trade history of the bot
        self.hist_trade['cash'] = self.cash  # All the historical value of the bot
        self.hist_trade['value'] = self.cash  # All the historical cash of the bot
        self.hist_trade['var'] = 0 # All the historical variables of the bot

    def initiate(self, name_list: list):
        """
        Fill stock dataframe with the names of the stocks
        :param name_list: list with all names of the stocks
        """
        for name in name_list:
            self.stocks[name] = 0
            self.hist_trade[name] = 0

    def calc_worth(self, hist_data: pd.DataFrame):
        """
        Calculate worth of cash and all stocks combined
        :param hist_data: matrix of a set of historical values for the given stocks
        """
        worth = self.cash

        for i in self.stocks:
            stock_amount = self.stocks[i]
            stock_price_row = hist_data.iloc[-1]
            stock_price = stock_price_row[i]
            worth = worth + stock_amount * stock_price

        self.value = worth

    def buy(self, stock_ticker, hist_data):
        current_stock_price = hist_data.iloc[-1].loc[stock_ticker]
        stock_amount = math.floor(self.cash / current_stock_price)
        total_stock_value = stock_amount * current_stock_price
        self.stocks[stock_ticker] = self.stocks[stock_ticker] + stock_amount  # add stock
        self.cash = self.cash - total_stock_value  # subtract cash

        return stock_amount

    def sell(self, stock_ticker, hist_data):
        current_stock_price = hist_data.iloc[-1].loc[stock_ticker]
        total_stock_value = self.stocks[stock_ticker] * current_stock_price
        stock_amount = self.stocks[stock_ticker]
        self.stocks[stock_ticker] = 0
        self.cash = self.cash + total_stock_value

        return -1 * stock_amount

    def save_hist(self, ticker, stock_amount, date, var_data=0):
        """
        Save history for each time step
        :param ticker: name of stock
        :param stock_amount: amount of stock bought or sold (negative values is sold)
        :param date: the time stamp for this save
        :param var_data: the data where the decision was based on, e.g. RSI. = 0 if not specified
        """
        # Make new entry and fill with correct keys
        new_entry = pd.Series(self.stocks).astype('float64')
        for key in self.hist_trade.columns:
            new_entry[key] = 0
        new_entry['cash'] = self.cash
        new_entry['value'] = self.value
        new_entry['var'] = var_data
        new_entry[ticker] = stock_amount

        row_date = {0: date}
        self.hist_trade = pd.concat([self.hist_trade,
                                     pd.DataFrame(new_entry).transpose().rename(row_date)])
        self.hist_trade = self.hist_trade.rename_axis('Date')


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
        if isinstance(moving_average, int):
            return

        # This is temporary trade function (only works for 1 stock)
        # make new entry
        new_entry = pd.Series(self.stocks).astype('float64')
        new_entry['cash'] = 0
        new_entry['value'] = 0
        new_entry['var'] = 0
        for key in self.hist_trade.columns:
            new_entry[key] = 0

        key = moving_average.index[0]  # Get key from first stock
        current_value = hist_data.iloc[-1].values[0]  # select last value as current value

        # If the moving average is larger than the current value of the stock
        if moving_average.at[key] >= current_value:
            # If stock is not bought yet, buy
            if self.stocks[key] == 0:
                # Buy
                stock_amount = math.floor(self.cash / current_value)
                value = stock_amount * current_value
                self.stocks[key] = self.stocks[key] + stock_amount  # add stock
                self.cash = self.cash - value  # subtract cash

                new_entry[key] = stock_amount

        # If the moving average is smaller than the current value of the stock
        else:
            # If stock is already bought
            if self.stocks[key] != 0:
                # Sell
                value = self.stocks[key] * current_value
                stock_amount = self.stocks[key]
                self.stocks[key] = 0
                self.cash = self.cash + value

                new_entry[key] = -1*stock_amount

        # Calculate the total value of the portfolio
        self.calc_worth(hist_data)

        new_entry['cash'] = self.cash
        new_entry['value'] = self.value
        new_entry['var'] = moving_average.at[key]

        row_date = {0: hist_data.index[-1]}

        self.hist_trade = pd.concat([self.hist_trade,
                                     pd.DataFrame(new_entry).transpose().rename(row_date)])
        self.hist_trade = self.hist_trade.rename_axis('Date')

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
