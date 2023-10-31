import pandas as pd
import yfinance as yf
# import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import os.path
from dateutil.relativedelta import relativedelta

from sp500 import get_sp500_tickers
from bot import BotTemplate


class Simulator:

    def __init__(self, bot_array: list[BotTemplate], stock_ticker, start_date, end_date, interval):
        """
        Creates a simulator object using specified parameters
        :param bot_array: array with bot objects used in simulation
        :param stock_ticker: integer amount of stocks to simulate on (from S&P500)
        :param start_date: date to start simulation from (historical data)
        :param end_date: date to stop simulation (e.g. today)
        :param interval: interval between simulation data points
        """
        self.bot_array = bot_array
        self.stock_ticker = stock_ticker
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval

        # Amount of dataframe entries given to bots in first cycle
        self.history = 15

        self.stock_data = self.get_stock_data()
        print(self.stock_data)

    def simulate(self):
        """Runs the whole simulation by adding extra time steps and then calling sim_cycle"""
        # Initiate all bots by giving them the stocks where they are going to get the data from
        for i in range(len(self.bot_array)):
            self.bot_array[i].initiate(self.stock_data.columns.tolist())

        # Run all sim cycles by adding a time datapoint in each cycle
        for i in range(self.history, len(self.stock_data.index)):
            self.sim_cycle(self.stock_data.iloc[:i])

        # Plot the graphs using plotly
        self.plot_value_graphs()
        self.plot_rsi_graphs()
        self.plot_mov_avg_graphs()

    def sim_cycle(self, current_stock_data):
        """Everything that happens during one cycle of the simulation"""
        # Looping over all the bots and giving them the current stock data, so they can trade
        for i in range(len(self.bot_array)):
            self.bot_array[i].trade(current_stock_data)

    def get_stock_data(self):
        """Gets stock data from yahoo finance and puts it in a dataframe"""
        # If stock_ticker is number: get first x amount of stocks from S&P500
        if isinstance(self.stock_ticker, int):
            # Get the first x amount of tickers from the S&P500 index
            tickers = get_sp500_tickers(self.stock_ticker)

        # Else it is a string, so use the specified stock_ticker and add ^GSPC
        else:
            tickers = [self.stock_ticker, "^GSPC"]

        # Generate a filename based on the amount of stocks, the interval and the start and end date
        filename = str(str(self.stock_ticker) + "_" + self.interval + "_" +
                       self.start_date.strftime("%m-%d-%Y") + "_" +
                       self.end_date.strftime("%m-%d-%Y") + ".csv")

        # Check if that csv file already exists, which means that the data has been requested before
        if not self.load_df(filename).empty:
            # Load the data from this existing csv file into a dataframe and return it
            return self.load_df(filename)
        else:
            # If it doesn't exist yet: request the data and save it into a csv file for later use
            stock_data = self.download_stock_data_loop(tickers, self.start_date, self.end_date, self.interval)
            self.save_df(stock_data, filename)
            return stock_data

    def download_stock_data_loop(self, tickers, start_date, end_date, interval):
        """Downloads stock data from yahoo finance using loops if more than max data_amount per request is needed"""
        # Create a list where the dataframes will be stored that have to be concatenated
        df_list = list()

        # Calculate the time between the start and end date in days
        timespan = end_date - start_date
        days = timespan.days

        # The maximum amount of data that can be requested depends on the interval
        if interval == "1m":
            # Max for interval of 1 minute is 7 days of data, so if less just return data from one request
            if days <= 7:
                return self.read_price_data(tickers, start_date, end_date, interval)
            else:
                # Divide the total time up into segments of 7 days (max request time)
                current_start_date = start_date
                current_end_date = current_start_date + relativedelta(days=7)

                # While not yet all the timespan has been covered: download all data for 7 days, then go to next 7 days
                while current_end_date < end_date:
                    df = self.read_price_data(tickers, current_start_date, current_end_date, interval)
                    df_list.append(df)
                    current_start_date = current_end_date
                    current_end_date = current_start_date + relativedelta(days=7)

                # If total timespan is not a multiple of 7 days the rest of the time still has to be downloaded
                if current_start_date != end_date:
                    df = self.read_price_data(tickers, current_start_date, end_date, interval)
                    df_list.append(df)

        elif interval == "2m" or interval == "5m" or interval == "15m" or interval == "30m" or interval == "60m" \
                or interval == "90m" or interval == "1h":
            # Max for interval lower than 1 day is 60 days of data, so if less just return data from one request
            if days <= 60:
                return self.read_price_data(tickers, start_date, end_date, interval)
            else:
                # Divide the total time up into segments of 60 days (max request time)
                current_start_date = start_date
                current_end_date = current_start_date + relativedelta(days=60)

                # While not all the timespan has been covered: download all data for 60 days, then go to next 60 days
                while current_end_date < end_date:
                    df = self.read_price_data(tickers, current_start_date, current_end_date, interval)
                    df_list.append(df)
                    current_start_date = current_end_date
                    current_end_date = current_start_date + relativedelta(days=60)

                # If there is still a bit of not downloaded time left: request the data for the rest of the time
                if current_start_date != end_date:
                    df = self.read_price_data(tickers, current_start_date, end_date, interval)
                    df_list.append(df)

        # All intervals of 1 day or more can just download all data at once, so return the data from that request
        else:
            return self.read_price_data(tickers, start_date, end_date, interval)

        # Concatenate all the individual dataframes from the list into one dataframe and return it
        return pd.concat(df_list)

    def plot_value_graphs(self):
        """Plots the value of all bots over time together with the value if stock was bought and held the whole time"""
        # Looping over all the bots and plot the value of the bots in a graph
        df_bot_values = pd.DataFrame()
        fig = go.Figure()
        for bot in self.bot_array:
            df_bot_values['date'] = list(bot.hist_trade.index.values)
            fig.add_trace(
                go.Scatter(x=df_bot_values['date'], y=bot.hist_trade['value'],
                           name=str(bot.__class__.__name__ + " " + str(bot.alfa)))
            )

        # Getting stock data to plot value if stocks bought at beginning and not sold & normalize to start_cash
        df_bot_values[self.stock_data.columns[0]] = self.stock_data[self.stock_data.columns[0]]\
            .tail(len(df_bot_values)).values
        df_bot_values[self.stock_data.columns[0]] = \
            df_bot_values[self.stock_data.columns[0]] * (100000 / self.stock_data.iat[self.history - 1, 0])

        # Add the stock price as a line in the plot
        fig.add_scatter(x=df_bot_values['date'], y=df_bot_values[self.stock_data.columns[0]],
                        name=str("Stock Price of " + str(self.stock_data.columns[0])))

        # Set the title and axis labels of the plot
        fig.update_layout(title="Value over Time")
        fig.update_yaxes(title_text="<b>Value</b>")
        fig.update_xaxes(title_text="<b>Date</b>")

        fig.show()

    def plot_mov_avg_graphs(self):
        """Plots the moving averages of the BotMovingAverage bots together with the stock price"""
        # Looping over all the bots and plot the moving averages saved in hist_trade['var']
        df_bot_values = pd.DataFrame()
        fig = go.Figure()
        for bot in self.bot_array:
            df_bot_values['date'] = list(bot.hist_trade.index.values)
            # Check if class is of type BotMovingAverage and otherwise don't plot the moving average
            if bot.__class__.__name__ == "BotMovingAverage":
                fig.add_trace(
                    go.Scatter(x=df_bot_values['date'], y=bot.hist_trade['var'],
                               name=str('Moving Average of bot ' + str(bot.alfa)))
                )

        # Make the lines dotted, so the moving averages are distinguishable from the stock price line
        fig.update_traces(patch={"line": {"width": 2, "dash": 'dot'}})

        # Set title and axis titles of the graph
        fig.update_layout(title="Moving average & Stock Price over Time")
        fig.update_yaxes(title_text="<b>Stock Price</b>")
        fig.update_xaxes(title_text="<b>Date</b>")

        # Getting stock price data
        df_bot_values[self.stock_data.columns[0]] = self.stock_data[self.stock_data.columns[0]] \
            .tail(len(df_bot_values)).values

        # Plotting the stock price over time
        fig.add_scatter(x=df_bot_values['date'], y=df_bot_values[self.stock_data.columns[0]],
                        name=str("Stock Price of " + str(self.stock_data.columns[0])))

        fig.show()


    def plot_rsi_graphs(self):
        """Plots the RSI calculation of a bot over time together with the stock price over time"""
        # Create a dataframe with the stock price over time in it and the dates, handy for plotting
        df_stock_price = pd.DataFrame(self.stock_data[self.stock_data.columns[0]])
        df_stock_price['Date'] = self.stock_data.index.values

        # Create figure with secondary y-axis
        fig = make_subplots(rows=2, cols=1)

        # Looping over all the bots and add var_data to the plot
        for bot in self.bot_array:
            # Check if class is of type BotRSI and otherwise don't plot the RSI
            if bot.__class__.__name__ == "BotRSI":
                fig.add_trace(
                    go.Scatter(x=df_stock_price['Date'], y=bot.hist_trade['var'],
                               name=str('RSI of bot ' + str(bot.alfa))), row=2, col=1
                )

        # Add stock price graph to be able to view it together with the RSI
        fig.add_trace(
            go.Scatter(x=df_stock_price['Date'], y=df_stock_price[self.stock_data.columns[0]],
                       name=str("Stock Price of " + str(self.stock_data.columns[0]))), row=1, col=1
        )

        # Set the RSI axes to range from 0 to 100
        fig.update_yaxes(range=[0, 100], row=2, col=1)

        # Add horizontal RSI lines
        fig.add_hline(y=70, line_width=2, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_width=2, line_dash="dash", line_color="green", row=2, col=1)

        # Add figure title
        fig.update_layout(title_text="RSI & Stock Price over Time")

        # Set y-axes & x-axes titles
        fig.update_yaxes(title_text="<b>RSI</b>", row=2, col=1)
        fig.update_yaxes(title_text="<b>Stock Price</b>", row=1, col=1)
        fig.update_xaxes(title_text="<b>Date</b>")

        fig.show()

    def read_price_data(self, stock_symbol, start_date, end_date, interval):
        """Imports price data from Yahoo Finance"""
        try:
            stock_data = yf.download(stock_symbol, start_date, end_date, interval=interval)
        except:
            return None

        prices = stock_data.loc[:, "Adj Close"]
        prices = prices.ffill()

        return prices

    def save_df(self, df: pd.DataFrame, filename):
        """Saves a dataframe as a cvs file and returns it"""
        df.to_csv(filename)

    def load_df(self, filename):
        """Loads a dataframe from a csv file and returns it"""
        if not os.path.isfile(filename):
            return pd.DataFrame

        return pd.read_csv(filename, index_col=0)
