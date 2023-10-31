from simulator import Simulator
from bot_rsi import BotRSI
from bot_dhl import BotDHL
from bot_movavg import BotMovingAverage


class Trainer:
    def __init__(self, bot_amount: int, stock_ticker, start_cash, start_date, end_date, interval):
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
        # self.bot_list = [BotMovingAverage(start_cash, stock_amount, i) for i in range(10, bot_amount + 10)]

        self.bot_list = list()

        # Put a bot of each type into the list until you reach bot_amount
        bot_type = 0
        for i in range(bot_amount):
            if bot_type > 2:
                bot_type = 0

            if bot_type == 0:
                self.bot_list.append(BotDHL(start_cash, 5 + round((i + 1) / 3)))
            elif bot_type == 1:
                self.bot_list.append(BotRSI(start_cash, 7 + round((i + 1) / 3)))
            elif bot_type == 2:
                self.bot_list.append(BotMovingAverage(start_cash, 2 + round((i + 1) / 3)))

            bot_type = bot_type + 1

        # Create the sim
        self.sim = Simulator(self.bot_list, stock_ticker, start_date, end_date, interval)

    def simulate(self):
        """
        Simulates for all given bots and extracts the data
        """
        self.sim.simulate()

        # Temporary code
        for bot in self.bot_list:
            print(bot.alfa, ":", bot.value)
            print("Historical trade data: \n", bot.hist_trade)

