# -*- coding=utf-8 -*-
import numpy as np
import pandas as pd
import tushare as ts


def save_data_as_hdf5():
    np.random.seed(50)
    data = np.random.randn(500000, 10)
    # print(data.shape)
    data = pd.DataFrame(data)
    print(data.head())
    # 1- 将数据存储到 HDF5 中
    hdf5 = pd.HDFStore('../data/random_number.h5', 'w')
    hdf5['data'] = data
    hdf5.close()

    # 2- 读取 HDF5 数据。类型为：pandas.io.pytables.HDFStore
    hdf5 = pd.HDFStore('../data/random_number.h5', 'r')
    data = hdf5['data']
    print(data.head())
    hdf5.close()


if __name__ == '__main__':
    save_data_as_hdf5()
