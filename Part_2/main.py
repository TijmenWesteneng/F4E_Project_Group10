import datetime
from dateutil.relativedelta import relativedelta

from trainer import *

bot_amount = 5
stock_amount = 2
start_cash = 100000
start_date = datetime.date(2023, 10, 23) - relativedelta(years=1)
end_date = datetime.date(2023, 10, 23)
interval = "1d"

trainer = Trainer(bot_amount, stock_amount, start_cash, start_date, end_date, interval)

trainer.simulate()
