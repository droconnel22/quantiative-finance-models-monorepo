import pandas as pd
from pandas import Series
from random import gauss
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

if __name__ == '__main__':

    nums = [gauss(0, 1) for _ in range(20000)]
    data = Series(nums)

    plot_acf(data)
    plt.show()

    plt.hist(data, bins=500)
    plt.show()

