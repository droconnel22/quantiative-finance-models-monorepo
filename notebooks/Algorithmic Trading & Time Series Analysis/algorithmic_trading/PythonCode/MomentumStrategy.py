import yfinance as yf
import backtrader as bt
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np


def calculate_momentum(data):
    log_data = np.log(data)
    x_data = np.arange(len(log_data))
    beta, _, rvalue, _, _ = linregress(x_data, log_data)
    # we have to annualize the slope
    # there are 252 trading days in a year
    return ((1+beta)**252) * (rvalue**2)


class Momentum(bt.Indicator):
    # every trading day has a momentum parameter
    # except for the first 90 days
    lines = ('momentum_trend',)
    params = (('period', 90),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        returns = np.log(self.data.get(size=self.params.period))
        x = np.arange(len(returns))
        beta, _, rvalue, _, _ = linregress(x, returns)
        annualized = (1 + beta) ** 252
        self.lines.momentum_trend[0] = annualized * rvalue ** 2


class MomentumStrategy(bt.Strategy):

    def __init__(self):
        self.counter = 0
        self.indicators = {}
        self.sorted_data = []
        # we store the SP500 (this is the index) data as the first item of the dataset
        self.spy = self.datas[0]
        # all the other stocks (present in SP500)
        self.stocks = self.datas[1:]

        for stock in self.stocks:
            self.indicators[stock] = {}
            self.indicators[stock]['momentum'] = Momentum(stock.close, period=90)
            self.indicators[stock]['sma100'] = bt.indicators.\
                SimpleMovingAverage(stock.close, period=100)
            self.indicators[stock]['atr20'] = bt.indicators.ATR(stock, period=20)

        # SMA for SP500 index - because we open long positions when the SP500 index
        # is above it's SMA(200) BULLISH MARKET
        self.sma200 = bt.indicators.MovingAverageSimple(self.spy.close, period=200)

    def prenext(self):
        # count the number of days elapsed
        self.next()

    def next(self):
        # a week has passed so we have to make trades
        if self.counter % 5 == 0:
            self.rebalance_portfolio()
        if self.counter % 10 == 0:
            # 2 weeks have passed
            self.update_positions()

        self.counter += 1

    def rebalance_portfolio(self):

        self.sorted_data = list(filter(lambda stock_data: len(stock_data) > 100, self.stocks))
        # sort the SP500 stocks based on momentum
        self.sorted_data.sort(key=lambda stock: self.indicators[stock]['momentum'][0])
        num_stocks = len(self.sorted_data)

        # sell stocks (close the long positions) - top 20%
        for index, single_stock in enumerate(self.sorted_data):
            # we can check whether are there open positions
            if self.getposition(self.data).size:
                # if the stock is not in the top 20% then close the long position
                # sell the stock if it's price falls below its 100 days MA
                if index > 0.2 * num_stocks or single_stock < self.indicators[single_stock]['sma100']:
                    self.close(single_stock)

        # we open long positions when the SMA is below the SP500 index
        if self.spy < self.sma200:
            return

        # consider the top 20% of the stocks and buy accordingly
        for index, single_stock in enumerate(self.sorted_data[:int(0.2 * num_stocks)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash > 0 and not self.getposition(self.data).size:
                size = value * 0.001 / self.indicators[single_stock]["atr20"]
                self.buy(single_stock, size=size)

    def update_positions(self):
        num_stocks = len(self.sorted_data)

        # top 20% momentum range
        for index, single_stock in enumerate(self.sorted_data[:int(0.2 * num_stocks)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash > 0:
                size = value * 0.001 / self.indicators[single_stock]["atr20"]
                self.order_target_size(single_stock, size)


if __name__ == '__main__':
    stocks = []
    cerebro = bt.Cerebro()

    with open("companies_all") as file_in:
        for line in file_in:
            stocks.append(line.strip('\n'))
            try:
                df = pd.read_csv(line.strip('\n'), parse_dates=True, index_col=0)
                if len(df) > 100:
                    cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False))
            except FileNotFoundError:
                pass

    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    # this is how we attach the strategy we have implemented
    cerebro.addstrategy(MomentumStrategy)

    cerebro.broker.set_cash(100000)
    # commission fee is 1%
    cerebro.broker.setcommission(0.01)

    print('Initial capital: $%.2f' % cerebro.broker.getvalue())
    results = cerebro.run()

    print(f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}")
    print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
    print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
    print('Capital: $%.2f' % cerebro.broker.getvalue())