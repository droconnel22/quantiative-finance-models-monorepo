import matplotlib.pyplot as plt
from random import gauss
from pandas import Series
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf

if __name__ == '__main__':

    w = [gauss(0, 1) for _ in range(20000)]
    x = [0 for _ in range(20000)]

    # create the time series
    for t in range(2, len(x)):
        x[t] = w[t] + 0.1*w[t-1] + 0.4*w[t-2]

    model = ARIMA(x, order=(0, 0, 5))
    model = model.fit()

    # residual series = actual values - predicted values
    plot_acf(model.resid)
    plt.show()

    print(model.summary())
