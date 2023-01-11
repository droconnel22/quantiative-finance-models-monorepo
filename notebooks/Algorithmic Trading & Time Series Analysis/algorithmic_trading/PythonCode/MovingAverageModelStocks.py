import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf


def download_data(stock, start, end):
    stock_data = {}
    ticker = yf.download(stock, start, end)
    stock_data['Price'] = ticker['Adj Close']
    return pd.DataFrame(stock_data)


if __name__ == '__main__':

    start_date = '2005-01-05'
    end_date = '2010-01-05'

    stock_data = download_data('MSFT', start_date, end_date)

    stock_returns = np.log(stock_data['Price'] / stock_data['Price'].shift(1))
    stock_returns = stock_returns.dropna()

    model = ARIMA(stock_returns.values, order=(0, 0, 2))
    model = model.fit()

    plot_acf(model.resid, lags=50)
    plt.show()
