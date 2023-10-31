import pandas as pd
import math

from bot import BotTemplate


class BotMovingAverage(BotTemplate):
    def __init__(self, start_cash, window_size: int):
        """
        Creates a specific trading strategy bot
        :param start_cash: double of amount of cash that the bot starts with in the beginning
        :param window_size: variable upon which the bot behaves differently
        """
        super().__init__(start_cash)  # Inherit the class BotTemplate
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
