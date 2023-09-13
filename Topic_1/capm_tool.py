import numpy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def capm_calculator(index_share_df):
    # Change dataframe (table) from price levels to returns (in percentages)
    df = index_share_df.pct_change()*100
    df = df.dropna()

    # Calculate covariance of dataframe and extract the covariance of the share and the market
    cov_matrix = df.cov()
    covariance_share_market = cov_matrix.iat[0, 1]

    # Calculate the variance and extract the variance of the market
    var_series = df.var()
    variance_market = var_series.iloc[0]

    # Calculate the beta
    capm_beta = covariance_share_market / variance_market

    print("The CAPM-beta of", df.columns.values[1], "compared to", df.columns.values[0], "is:", capm_beta)

    # Get returns as arrays so they can be plotted as a scatterplot
    index_returns = df[df.columns.values[0]].to_numpy()
    share_returns = df[df.columns.values[1]].to_numpy()

    # Calculating max_values so the plot can be centered around 0
    max_val = max(max(abs(index_returns)), max(abs(share_returns)))

    # Set the x and y limits
    plt.xlim(-max_val, max_val)
    plt.ylim(-max_val, max_val)

    # Generating scatter plot
    plt.scatter(index_returns, share_returns, marker='o')
    plt.xlabel(df.columns.values[0])
    plt.ylabel(df.columns.values[1])

    # Adding horizontal and vertical zero lines
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)

    # Get the beta as a trend line and plot it
    beta_scatter = np.polyfit(index_returns, share_returns, 1)
    trend_line = np.poly1d(beta_scatter)
    plt.plot(index_returns, trend_line(index_returns), "r--", linewidth=1)

    # Calculate the R^2
    corr_matrix = numpy.corrcoef(share_returns, trend_line(index_returns))
    correlation = corr_matrix[0, 1]
    r_2 = correlation**2
    print("The R^2 value of this beta is:", r_2)

    plt.show()

    df.plot()
    plt.show()


