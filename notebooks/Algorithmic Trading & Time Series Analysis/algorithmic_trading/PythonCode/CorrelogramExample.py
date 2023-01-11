import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

if __name__ == '__main__':

    # random noise
    data = np.random.random(100)
    plot_acf(data, lags=20)
    plt.show()

    # linear trend
    data = [i for i in range(100)]
    plot_acf(data, lags=20)
    plt.show()

    # repeating trend (seasonality)
    data = [1, 2, 3, 4, 5] * 10
    plot_acf(data, lags=20)
    plt.show()
