import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import numpy as np
import pandas as pd


def download_data(stock, start, end):
    data = {}
    ticker = yf.download(stock, start, end)
    data['price'] = ticker['Adj Close']
    return pd.DataFrame(data)


if __name__ == '__main__':

    start_date = datetime.datetime(2015, 1, 1)
    end_date = datetime.datetime(2020, 1, 1)

    stock_data = download_data('IBM', start_date, end_date)

    stock_data['return'] = np.log(stock_data['price'] / stock_data['price'].shift(1))
    stock_data['move'] = stock_data['price'] - stock_data['price'].shift(1)

    # average then the 0 values do not count
    stock_data['up'] = np.where(stock_data['move'] > 0, stock_data['move'], 0)
    stock_data['down'] = np.where(stock_data['move'] < 0, stock_data['move'], 0)

    # RS
    stock_data['average_gain'] = stock_data['up'].rolling(14).mean()
    stock_data['average_loss'] = stock_data['down'].abs().rolling(14).mean()

    RS = stock_data['average_gain'] / stock_data['average_loss']

    stock_data['rsi'] = 100.0 - (100.0 / (1.0 + RS))

    stock_data = stock_data.dropna()

    print(stock_data)
    plt.plot(stock_data['rsi'])
    plt.show()

