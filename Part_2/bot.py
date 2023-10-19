import numpy as np


class BotTemplate:
    def __init__(self, start_cash, stock_size, threshold):
        self.cash = start_cash
        self.stocks = np.zeros(stock_size)
        self.alfa = threshold

    def trade(self, hist_data):
        if hist_data[0] > self.alfa:
            return 'buy'
        else:
            return 'sell'
