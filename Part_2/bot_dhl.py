import pandas as pd
from bot import BotTemplate


class BotDHL(BotTemplate):
    def __init__(self, start_cash, stock_size: int, window_size: int):
        """
        Creates a bot with daily high low trading strategy
        :param start_cash: double of amount of cash that the bot starts with in the beginning
        :param stock_size: integer of the amount of unique stocks the program will feed to the bot
        :param window_size: integer of the length of the 'day'
        """
        super().__init__(start_cash, stock_size)  # Inherit the class BotTemplate
        self.last_daily_low = 0
        self.last_daily_high = 0
        self.alfa = window_size
        self.last_window_check = 0
        self.is_first = 1

    def trade(self, hist_data: pd.DataFrame):
        """
        Makes trading decisions based on the incoming historical data
        :param hist_data: matrix of a set of historical values for the given stocks
        """
        key = hist_data.columns[0]  # first column key
        current_date = hist_data.index[-1]  # current date
        stock_amount = 0  # stock amount init

        # if given dataframe length is smaller than window size, skip trade
        if len(hist_data) < self.alfa:
            return

        # if we traded for a full window recalculate the daily high low
        if self.last_window_check > self.last_window_check or self.is_first:
            last_day = hist_data.iloc[-(self.alfa+1):-1]  # select last day
            self.dhl(last_day)  # recalculate last daily high low
            self.is_first = 0  # reset is first time

        # if the value now is more then the last daily high, buy
        if hist_data.iloc[-1, 0] > self.last_daily_high:
            if self.stocks[key] == 0:
                stock_amount = self.buy(key, hist_data)

        # if the value now is less then the last daily low, sell
        if hist_data.iloc[-1, 0] < self.last_daily_low:
            if self.stocks[key] != 0:
                stock_amount = self.sell(key, hist_data)

        self.calc_worth(hist_data)
        self.save_hist(key, stock_amount, current_date)  # save history of bot
        self.last_window_check = self.last_window_check + 1  # increase last window check

    def dhl(self, hist_data: pd.DataFrame):
        """
        Calculates the daily high low for a given time period
        :param hist_data: matrix of a set of historical values for a given stock
        """
        self.last_daily_high = self.last_daily_low = hist_data.iloc[0, 0]  # reset values

        for value in hist_data.iloc[1:, 0]:
            if value > self.last_daily_high:
                self.last_daily_high = value
            if value < self.last_daily_low:
                self.last_daily_low = value

        self.last_window_check = 0

