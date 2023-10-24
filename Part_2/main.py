from trainer import *

bot_amount = 1
stock_amount = 1
start_cash = 100000
start_date = 0
end_date = 0
interval = 0

trainer = Trainer(bot_amount, stock_amount, start_cash, start_date, end_date, interval)

trainer.simulate()
