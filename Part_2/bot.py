import numpy as np


class BotTemplate:
    def __init__(self, start_cash, stock_size, threshold):
        """
        Creates a Bot that makes a trading decision based on the incoming data
        :param start_cash: double of amount of cash that the bot starts with in the beginning
        :param stock_size: integer of the amount of unique stocks the program will feed to the bot
        :param threshold: double of the threshold value for making trading decisions
        """
        self.cash = start_cash
        self.stocks = np.zeros(stock_size)
        self.alfa = threshold

    def trade(self, hist_data):
        """
        Makes trading decisions based on the incoming historical data
        :param hist_data: matrix of a set of historical values for the given stocks
        """
        if hist_data[0] > self.alfa:
            return 'buy'
        else:
            return 'sell'
