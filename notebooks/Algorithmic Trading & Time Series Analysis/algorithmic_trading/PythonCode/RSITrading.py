import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import pandas as pd


class MovingAverageRSIStrategy:

    def __init__(self, capital, stock, start, end, short_period, long_period):
        self.data = None
        self.is_long = False
        self.short_period = short_period
        self.long_period = long_period
        self.capital = capital
        self.equity = [capital]
        self.stock = stock
        self.start = start
        self.end = end

    def download_data(self):
        stock_data = {}
        ticker = yf.download(self.stock, self.start, self.end)
        stock_data['price'] = ticker['Adj Close']
        self.data = pd.DataFrame(stock_data)

    def construct_signals(self):
        self.data['short_ma'] = self.data['price'].ewm(span=self.short_period).mean()
        self.data['long_ma'] = self.data['price'].ewm(span=self.long_period).mean()
        self.data['move'] = self.data['price'] - self.data['price'].shift(1)
        self.data['up'] = np.where(self.data['move'] > 0, self.data['move'], 0)
        self.data['down'] = np.where(self.data['move'] < 0, self.data['move'], 0)
        self.data['average_gain'] = self.data['up'].rolling(14).mean()
        self.data['average_loss'] = self.data['down'].abs().rolling(14).mean()
        relative_strength = self.data['average_gain'] / self.data['average_loss']
        self.data['rsi'] = 100.0 - (100.0 / (1.0 + relative_strength))
        self.data = self.data.dropna()
        print(self.data)

    def plot_signals(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.data['price'], label='Stock Price')
        plt.plot(self.data['short_ma'], label='Short MA', color='blue')
        plt.plot(self.data['long_ma'], label='Long MA', color='green')
        plt.title('Moving Average (MA) Crossover Trading Strategy with RSI')
        plt.xlabel('Date')
        plt.ylabel('Stock Price')
        plt.show()

    def simulate(self):
        price_when_buy = 0

        for index, row in self.data.iterrows():
            if row['short_ma'] < row['long_ma'] and self.is_long:
                self.equity.append(row['price'] * self.capital / price_when_buy)
                self.is_long = False
            elif row['short_ma'] > row['long_ma'] and not self.is_long \
                    and row['rsi'] < 30:
                price_when_buy = row['price']
                self.is_long = True

    def plot_equity(self):
        plt.figure(figsize=(12, 6))
        plt.title('Equity Curve')
        plt.plot(self.equity, label='Stock Price', color='green')
        plt.xlabel('Date')
        plt.ylabel('Capital ($)')
        plt.show()

    def show_stats(self):
        print("Profit of the trading strategy: %.2f%%" % (
                (float(self.equity[-1]) - float(self.equity[0])) /
                float(self.equity[0]) * 100))
        print("Actual capital: %0.2f" % self.equity[-1])
        returns = (self.data['price'] - self.data['price'].shift(1)) / self.data['price'].shift(1)
        ratio = returns.mean() / returns.std() * np.sqrt(252)
        print('Sharpe ratio: %.2f' % ratio)


if __name__ == '__main__':
    start_date = datetime.datetime(2010, 1, 1)
    end_date = datetime.datetime(2020, 1, 1)

    model = MovingAverageRSIStrategy(100, 'IBM', start_date, end_date, 40, 150)
    model.download_data()
    model.construct_signals()
    model.plot_signals()
    model.simulate()
    model.plot_equity()
    model.show_stats()
