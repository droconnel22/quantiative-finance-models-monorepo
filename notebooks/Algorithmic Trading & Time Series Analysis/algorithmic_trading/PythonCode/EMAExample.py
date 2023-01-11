import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import pandas as pd


def download_data(stock, start, end):
    data = {}
    ticker = yf.download(stock, start, end)
    data['Price'] = ticker['Adj Close']
    return pd.DataFrame(data)


def construct_signals(data, short_period, long_period):
    data['Short EMA'] = data['Price'].ewm(span=short_period, adjust=False).mean()
    data['Long EMA'] = data['Price'].ewm(span=long_period, adjust=False).mean()


def plot_data(data):
    plt.figure(figsize=(12, 6))
    plt.plot(data['Price'], label='Stock Price')
    plt.plot(data['Short EMA'], label='Short EMA', color='red')
    plt.plot(data['Long EMA'], label='Long EMA', color='blue')
    plt.title('Exponential Moving Average (SMA) Indicators')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.show()


if __name__ == '__main__':

    start_date = datetime.datetime(2010, 1, 1)
    end_date = datetime.datetime(2020, 1, 1)

    stock_data = download_data('IBM', start_date, end_date)
    construct_signals(stock_data, 50, 200)
    stock_data = stock_data.dropna()
    plot_data(stock_data)
