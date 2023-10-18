import datetime
from dateutil.relativedelta import relativedelta
from datareader import read_price_data
import matplotlib.pyplot as plt
import numpy as np
from white_noise import get_white_noise_array


stock_symbol = "F"  # Stock symbol

# Specify start and end dates
start_date = datetime.date.today() - relativedelta(days=183)
end_date = datetime.date.today()
interval = '1d'  # Date interval, by default daily ('1d')

company_name, price_data = read_price_data(stock_symbol, start_date, end_date, interval=interval)
price_data_mean = np.mean(price_data)
price_data_std_dev = np.std(price_data)
white_noise = get_white_noise_array(price_data.size, price_data_mean, price_data_std_dev)

shifted_price_data = np.insert(np.delete(price_data, -1), 0, 0)
shifted_white_noise = np.insert(np.delete(white_noise, -1), 0, 0)

# Get correlation coefficient
corr_matrix_price = np.corrcoef(price_data, shifted_price_data)
corr_price = corr_matrix_price[1, 0]
corr_matrix_white = np.corrcoef(white_noise, shifted_white_noise)
corr_white = corr_matrix_white[1, 0]

# Create subplot
fig = plt.figure()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

# Generating scatter plot
ax1.scatter(price_data, shifted_price_data, marker='.')
ax2.scatter(white_noise, shifted_white_noise, marker='.')

# Adding horizontal and vertical zero lines
ax1.axhline(0, color='black', linewidth=0.5)
ax1.axvline(0, color='black', linewidth=0.5)
ax2.axhline(0, color='black', linewidth=0.5)
ax2.axvline(0, color='black', linewidth=0.5)

# Set plot title that includes company name
ax1.set_title(company_name + ": Successive daily returns - 0.5 years")
ax2.set_title("White noise: Successive daily returns - 0.5 years")

# Add corr_coeff to the plot
ax1.text(-3 * price_data_std_dev, 2*price_data_std_dev, "Correlation: " + str("%.3f" % corr_price))
ax2.text(-3 * price_data_std_dev, 2*price_data_std_dev, "Correlation: " + str("%.3f" % corr_white))

plt.show()


