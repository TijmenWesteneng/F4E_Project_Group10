import pandas as pd
from simulator import Simulator
from bot import *


class Trainer:
    def __init__(self, bot_amount: int, stock_amount: int, start_cash, start_date, end_date, interval):
        """
        Creates a Trainer that has one simulator with alot of bots
        :param bot_amount: integer amount of bots that are tested
        :param stock_amount: integer amount of stock to simulate on (from S&P500)
        :param start_cash: amount of cash to start with
        :param start_date: date to start the simulator
        :param end_date: date to end the simulator
        :param interval: interval between time steps e.g. 1h or 1d
        """

        # Create the bots with a threshold
        self.bot_list = [BotMovingAverage(start_cash, stock_amount, i) for i in range(2, bot_amount + 2)]

        # Create the sim
        self.sim = Simulator(self.bot_list, stock_amount, start_date, end_date, interval)

    def simulate(self):
        """
        Simulates for all given bots and extracts the data
        """
        self.sim.simulate()

        # Temporary code
        for bot in self.bot_list:
            print(bot.alfa, ":", bot.value)
            print("Historical trade data: ", bot.hist_trade)
            print("Historical cash data: ", bot.hist_cash)
            print("Historical value data: ", bot.hist_value)
