# -*- coding: utf-8 -*-
#* Author: liuxun@2020.01.03

import pandas as pd
from matplotlib import pyplot

def readCsv():

    data = pd.read_csv("/home/lewisliu/Downloads/daily-total-female-births.csv", header = 0, parse_dates = [0], index_col = 0, squeeze = True)

    print(type(data))
    print(data.tail(10))
    print(data.size)
    # print(data['1959-01'])

    print(data.describe())
    pyplot.plot(data)
    pyplot.show()


    dataFrame = pd.DataFrame(data)
    print(dataFrame.head())


if __name__ == "__main__":
    readCsv()