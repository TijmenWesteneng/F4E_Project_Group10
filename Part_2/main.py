from bot import *

# make bot
test = BotTemplate(100000, 10)

# test if bot works
print(test.stocks)

# create a couple of bots systematically
BOT_object = []
for i in range(5):
    BOT = BotTemplate(100000, i)
    BOT_object.append(BOT)

# see if creating bots systematically works
for i in range(5):
    print(BOT_object[i].stocks)
