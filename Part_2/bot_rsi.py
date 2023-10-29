from bot import BotTemplate
import pandas as pd


class BotRSI(BotTemplate):

    def __init__(self, start_cash, stock_size: int, window_size: int):
        """
        Creates a specific trading strategy bot
        :param start_cash: double of amount of cash that the bot starts with in the beginning
        :param stock_size: integer of the amount of unique stocks the program will feed to the bot
        """
        # Inherit the class BotTemplate
        super().__init__(start_cash, stock_size)
        self.alfa = window_size

    def trade(self, hist_data: pd.DataFrame):
        rsi = self.calculate_rsi(hist_data)
        stock_ticker = hist_data.columns[0]

        # If relative strength index <= 30, means oversold: so buy
        if rsi <= 30:
            stock_amount = self.buy(stock_ticker, hist_data)

        # If relative strength index >= 70, means overbought: so sell
        elif rsi >= 70:
            stock_amount = self.sell(stock_ticker, hist_data)

        # Else: not overbought or oversold, so do nothing
        else:
            stock_amount = 0

        self.calc_worth(hist_data)

        current_date = hist_data.index[-1]
        self.save_hist(stock_ticker, -1 * stock_amount, current_date, rsi)

    def calculate_rsi(self, hist_data: pd.DataFrame):
        """Calculates the RSI of a set of stock_data values and returns the current RSI"""
        # Only extract the first stock column from the historic data & reverse it for moving average calculations
        hist_data = hist_data[hist_data.columns[0]]
        hist_data = hist_data[::-1]

        # Get the row-to-row change of historic data as a dataframe and remove NaNs
        change_data = hist_data.diff()
        change_data.dropna(inplace=True)

        # Make copies of the change_data to use for up and down
        change_up = change_data.copy()
        change_down = change_data.copy()

        # Replace all values of change_up lower than 0 with 0 and vice-versa
        change_up[change_up < 0] = 0
        change_down[change_down > 0] = 0

        # Make sure window is never be bigger than the current available data
        if len(hist_data.index) < self.alfa:
            window = len(hist_data.index) - 1
        else:
            window = self.alfa

        # Calculate the rolling averages
        avg_up = change_up.rolling(window).mean()
        avg_down = change_down.rolling(window).mean().abs()

        # Calculate the RSI over time
        rsi = 100 - 100 / (1 + (avg_up / avg_down))

        # Return current value of the RSI
        return rsi.iloc[window - 1]
