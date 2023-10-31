import datetime
from dateutil.relativedelta import relativedelta

from trainer import Trainer

bot_amount = 15  # Amount of bots you want to test
stock_ticker = "ASML"  # Stock ticker you want data from. Specify a number if you want the first x stocks from S&P500
start_cash = 100000  # Amount of cash all the bots get at the beginning
end_date = datetime.date(2023, 10, 31)  # End date of the dataset you want to simulate on
start_date = end_date - relativedelta(years=1)  # Start date of the dataset you want to simulate on (e.g. weeks=2)
interval = "1d"  # Interval requested dataset (e.g. 1m (1 minute), 1h (1 hour), 1d (1 day), 1mo (1 month), etc.)

trainer = Trainer(bot_amount, stock_ticker, start_cash, start_date, end_date, interval)

trainer.simulate()
