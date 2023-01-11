import datetime
import pandas as pd
import yfinance as yf
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import ParameterGrid
import matplotlib.pyplot as plt


def fetch_data(symbol, start, end):
    ticker = yf.download(symbol, start, end)
    return pd.DataFrame(ticker)


def calculate_rsi(data, period=14):
    data['move'] = data['Close'] - data['Close'].shift(1)
    data['up'] = np.where(data['move'] > 0, data['move'], 0)
    data['down'] = np.where(data['move'] < 0, data['move'], 0)
    data['average_gain'] = data['up'].rolling(period).mean()
    data['average_loss'] = data['down'].abs().rolling(period).mean()
    data['relative_strength'] = data['average_gain'] / data['average_loss']
    return 100.0 - (100.0 / (1.0 + data['relative_strength']))


def construct_signals(data, ma_period=60, rsi_period=14):
    data['SMA'] = data['Close'].rolling(window=ma_period).mean()
    # these are the 2 features
    data['trend'] = (data['Open'] - data['SMA']) * 100
    data['RSI'] = calculate_rsi(data, rsi_period) / 100
    # we need the target variables (labels)
    data['direction'] = np.where(data['Close'] - data['Open'] > 0, 1, -1)


if __name__ == '__main__':
    start_date = datetime.datetime(2018, 1, 1)
    end_date = datetime.datetime(2020, 1, 1)

    # EUR-USD currency pair
    currency_data = fetch_data('EURUSD=X', start_date, end_date)
    construct_signals(currency_data)

    currency_data = currency_data.dropna()

    X = currency_data[['trend', 'RSI']]
    y = currency_data['direction']

    # split the data into training and test set (80%-20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # model - we can find the right coefficients
    parameters = {'gamma': [10, 1, 0.1, 0.01, 0.001], 'C': [1, 10, 100, 1000, 10000]}
    grid = list(ParameterGrid(parameters))

    best_accuracy = 0
    best_parameters = None

    for p in grid:
        svm = SVC(C=p['C'], gamma=p['gamma'])
        svm.fit(X_train, y_train)
        predictions = svm.predict(X_test)

        if accuracy_score(y_test, predictions) > best_accuracy:
            best_accuracy = accuracy_score(y_test, predictions)
            best_parameters = p

    # we have found the best parameters
    model = SVC(C=best_parameters['C'], gamma=best_parameters['gamma'])
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    print('Accuracy of the model: %.2f' % accuracy_score(y_test, predictions))
    print(confusion_matrix(predictions, y_test))
