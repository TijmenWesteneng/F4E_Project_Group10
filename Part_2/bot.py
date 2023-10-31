import math
import pandas as pd


class BotTemplate:
    def __init__(self, start_cash):
        """
        Creates a Bot that makes a trading decision based on the incoming data
        :param start_cash: double of amount of cash that the bot starts with in the beginning
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