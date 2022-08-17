# -*- coding: utf-8 -*-
#* Author: liuxun@2020.01.03
from numpy import array
from keras.models import Sequential
from keras.layers import Dense
import pandas as pd
from matplotlib import pyplot

def testUnivarateTSF():
    #* univarate mlp example

    #* define dataset
    X = array([
        [10, 20, 30],
        [20, 30, 40],
        [30, 40, 50],
        [40, 50, 60]
    ])
    y = array([40, 50, 60, 70])

    #* define model
    model = Sequential()
    model.add(Dense(100, activation='relu', input_dim = 3))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    #* fit model
    model.fit(X, y, epochs = 2000, verbose = 0)

    #* demonstrate prediction
    x_input = array([50, 60, 70])
    x_input = x_input.reshape((1, 3))
    print(x_input)
    yhat = model.predict(x_input, verbose = 0)
    print(yhat)

def testLesson03():
    # data = pd.read_csv('/home/lewisliu/Downloads/shampoo.csv', header = 0, index_col = 0)
    # data.plot()
    # pyplot.show()
    data = pd.read_csv("/home/lewisliu/Downloads/daily-min-temperatures.csv", header = 0, index_col = 0, parse_dates = True, squeeze = True)
    print(data.head())
    # data.plot(style='k.')
    # pyplot.show()

    # groups = data.groupby(pd.Grouper(freq='A'))
    # years = pd.DataFrame()
    # for name, group in groups:
    #     years[name.year] = group.values
    # years.plot(subplots = True, legend = False)
    # pyplot.show()

    # data.hist()
    # pyplot.show()

    # data.plot(kind = 'kde')
    # pyplot.show()

    # groups = data.groupby(pd.Grouper(freq='A'))
    # years = pd.DataFrame()
    # for name, group in groups:
    #     years[name.year] = group.values
    # years.boxplot()
    # pyplot.show()

    # one_year = data['1990']
    # groups = one_year.groupby(pd.Grouper(freq='M'))
    # months = pd.concat([pd.DataFrame(x[1].values) for x in groups], axis = 1)
    # months = pd.DataFrame(months)
    # months.columns = range(1, 13)
    # months.boxplot()
    # pyplot.show()

    # groups = data.groupby(pd.Grouper(freq='A'))
    # years = pd.DataFrame()
    # for name, group in groups:
    #     years[name.year] = group.values
    # years = years.T
    # pyplot.matshow(years, interpolation=None, aspect='auto')
    # pyplot.show()

    # one_year = data['1990']
    # groups = one_year.groupby(pd.Grouper(freq='M'))
    # months = pd.concat([pd.DataFrame(x[1].values) for x in groups], axis = 1)
    # months = pd.DataFrame(months)
    # months.columns = range(1, 13)
    # pyplot.matshow(months, interpolation = None, aspect = 'auto')
    # pyplot.show()

    # pd.plotting.lag_plot(data)
    # pyplot.show()

    pd.plotting.autocorrelation_plot(data)
    pyplot.show()

if __name__ == "__main__":
    # testUnivarateTSF()
    testLesson03()