from trainer import *
import pandas as pd

"""
bot_amount = 1
stock_amount = 1
start_cash = 100000
start_date = 0
end_date = 0
interval = 0

trainer = Trainer(bot_amount, stock_amount, start_cash, start_date, end_date, interval)

trainer.simulate()
"""

from bot import *

bot = BotMovingAverage(100000, 1, 2)

data = {'A': [1, 2, 4, 5, 6]}
df = pd.DataFrame(data)

lst = ["A"]

bot.initiate(lst)
bot.calc_worth(df)

print(bot.value)
