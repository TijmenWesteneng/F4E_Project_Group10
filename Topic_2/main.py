import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import exp, sqrt, log
from scipy.stats import norm


def binomial_lattice(S0, K, r, v, T, n, call_put, exercise_policy):
    time_step = T / n

    # Calculate risk-free return rate per time step instead of per year
    r_per_time_step = math.e ** (r * time_step)

    # Compute u and d
    u = math.e ** (v * sqrt(time_step))
    d = math.e ** -(v * sqrt(time_step))

    # Compute p and q
    """ Fill in appropriate formulas"""
    p = (r_per_time_step - d) / (u - d)
    q = 0

    # Create empty matrix for stock prices
    stock_price = np.zeros((n + 1, n + 1))

    # Set initial stock price
    stock_price[0, 0] = S0

    # Fill matrix with stock prices per time step
    for i in range(1, n + 1):
        stock_price[i, 0] = stock_price[i - 1, 0] * u
        for j in range(1, i + 1):
            stock_price[i, j] = stock_price[i - 1, j - 1] * d

    # Transform numpy matrix into Pandas Dataframe
    df_stock_price = pd.DataFrame(data=stock_price)
    df_stock_price = df_stock_price.T

    # Create empty matrix for option values
    option_value = np.zeros((n + 1, n + 1))

    # For final time step, compute option value based on stock price and strike price
    for i in range(n + 1):
        if call_put == 'Call':
            if stock_price[n, i] <= K:
                option_value[n, i] = 0
            else:
                option_value[n, i] = stock_price[n, i] - K
        elif call_put == 'Put':
            if stock_price[n, i] >= K:
                option_value[n, i] = 0
            else:
                option_value[n, i] = K - stock_price[n, i]

    # Compute discount factor per time step
    discount = r_per_time_step - q

    # Recursively compute option value at time 0
    for i in range(n - 1, -1, -1):
        for j in range(i + 1):

            option_value[i, j] = (1 / discount) * (p * option_value[i + 1, j] + (1 - p) * option_value[i + 1, j + 1])

            if exercise_policy == 'American':
                if call_put == 'Call':
                    if option_value[i, j] < stock_price[i, j] - K:
                        option_value[i, j] = stock_price[i, j] - K
                elif call_put == 'Put':
                    if option_value[i, j] < K - stock_price[i, j]:
                        option_value[i, j] = K - stock_price[i, j]

    df_option_value = pd.DataFrame(data=option_value).T
    return option_value[0, 0], df_stock_price, df_option_value


def black_scholes(S0, K, v, T, r):
    r_maturity = math.e ** (r * T)
    d1 = math.log(S0 / (K / r_maturity), math.e) / v * sqrt(T) + v * sqrt(T) / 2
    d2 = d1 - v * sqrt(T)
    return (norm.cdf(d1) * S0) - (norm.cdf(d2) * (K / r_maturity))


# Test case: the following settings should yield an option price of 4.04
S0 = 100
K = 105
v = 0.1
T = 1
r = 0.05
n = 10
call_put = 'Call'
exercise_policy = 'European'

"""
S0 = 1  # Stock price
K = 1  # Strike price
v = 1  # Volatility
T = 1  # Time horizon
r = 1  # Risk-free rate
n = 10  # Number of time steps
call_put = 'Call'  # Option type ('Call' or 'Put')
exercise_policy = 'European'  # Option type ('European' or 'American')
"""

binomial_price, df, df_option = binomial_lattice(S0, K, r, v, T, n, call_put, exercise_policy)
black_scholes_price = black_scholes(S0, K, v, T, r)

print('Binomial lattice price: %.2f' % binomial_price)

if call_put == 'Call':
    print('Black-Scholes price: %.2f' % black_scholes_price)


# print(df)
# print(df_option)


def black_scholes_vega(S, K, T, r, v):
    d1 = (log(S / K) + (r + 0.5 * v ** 2) * T) / (v * sqrt(T))
    return S * norm.pdf(d1) * sqrt(T)


"""Implied volatility is found using the Newton-Raphson method"""


def compute_implied_volatility(true_price, S, K, r, T, n, call_put, exercise_policy):
    MAX_NO_ITERATIONS = 100
    MAX_VOL_UPDATE = 0.1
    ACCURACY = 1.0e-5

    implied_vol = .5  # Initial estimate for implied volatility

    for i in range(MAX_NO_ITERATIONS):
        # Compute price with binomial lattice, using current estimate for implied volatility
        model_price, _, _ = binomial_lattice(S, K, r, implied_vol, T, n, call_put, exercise_policy)

        # Compute difference between model price and market price (the root)
        diff = model_price - true_price

        # Terminate algorithm if desired precision has been hit
        if (abs(diff) < ACCURACY):
            return implied_vol

        # Update implied volatility based on vega and observed error
        vega = black_scholes_vega(S, K, T, r, implied_vol)

        implied_vol -= np.clip(diff / vega, -MAX_VOL_UPDATE, MAX_VOL_UPDATE)

    # If maximum number of iterations is hit, simply return best estimate so far
    return implied_vol


# Test case: the following settings should yield an implied volatility of 3.82%
# S0 = 100
# K = 100
# r = 0.05
# v = 0.1
# T = 1
# n = 10
# call_put = 'Call'
# exercise_policy = 'European'

# market_price = 5 # Set true market price of the option here

# Input parameters
# S0 = 1
# K = 1
# r = 1
# v = 1
# T = 1
# n = 10
# call_put = 'Call'
# exercise_policy = 'European'

# market_price = 1 # Set true market price of the option here

# Compute implied volatility using Newton-Raphson method
# implied_vol = compute_implied_volatility(market_price, S0, K, r, T, n, call_put, exercise_policy)

# Compute binomial lattice price with implied volatility
# binomial_price, _, _ = binomial_lattice(S0, K, r, implied_vol, T, n, call_put, exercise_policy)

# print ('Implied volatility: %.2f%%' % (implied_vol * 100))
# print ('True market price: %.2f' % market_price)
# print ('Binomial lattice price: %.2f' % binomial_price)

# Option chain implied volatility calculations
r = 0.46
n = 12
T = 1
SharePrice = [244.88, 12.59, 3086.58, 102.85, 244.88, 12.59, 3086.58, 102.85, 3086.58, 3086.58]
MarketPrice = [4.99, 0.01, 79.80, 1.21, 27.67, 3.49, 99.5, 5.05, 74, 77]  # Puts
StrikePrice = [225.00, 8, 3050, 97, 270, 16, 3120, 106, 3070.00, 3075.00]
call_put = 'Put'
exercise_policy = 'European'
implied_vol = []

for i in range(len(SharePrice)):
    implied_vol.append(compute_implied_volatility(MarketPrice[i], SharePrice[i], StrikePrice[i], r, T, n,
                                                  call_put, exercise_policy))

print(implied_vol)

# Option chain by binomial lattice
deviation = 0.01  # deviation from Market Price in relatively e.g. 0.01 is 1% difference
calculated_vol = []

start = 0.1
end = 1.2
step = 0.0001
for i in range(len(SharePrice)):
    for j in range(int(start/step), int(end/step) + 1):
        Vol_temp = j * step
        Market_temp, *_ = binomial_lattice(SharePrice[i], StrikePrice[i], r, Vol_temp, T, n, call_put, exercise_policy)
        if abs((Market_temp - MarketPrice[i])/MarketPrice[i]) < deviation:
            calculated_vol.append(Vol_temp)
            break

print(calculated_vol)

# Graph
# plt.scatter(x, y, marker='o')
plt.scatter(StrikePrice, implied_vol, marker='o')
plt.scatter(StrikePrice, calculated_vol, marker='x')
plt.xlabel('Strike level')
plt.ylabel('Implied volatility')
plt.show()
