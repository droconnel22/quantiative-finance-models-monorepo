import yfinance as yf
import pandas as pd
import numpy as np


def download_data(stocks, start_date, end_date):
    data = {}

    for stock in stocks:
        ticker = yf.download(stock, start_date, end_date)
        data[stock] = ticker['Adj Close']

    return pd.DataFrame(data)


if __name__ == '__main__':

    start = '2010-01-05'
    end = '2015-01-05'

    stock_data = download_data(['IBM', 'AAPL'], start, end)
    print(stock_data)

    # mean - expected value
    print('Mean of the IBM prices: %0.2f' % stock_data['IBM'].mean())

    # standard deviation (volatility)
    print('Standard deviation of the IBM prices: %0.2f' % stock_data['IBM'].std())

    # variance
    print('Variance of the IBM prices: %0.2f' % stock_data['IBM'].var())

    # covariance
    print(stock_data.cov())

    # correlation [-1,1]
    print(stock_data.corr())
