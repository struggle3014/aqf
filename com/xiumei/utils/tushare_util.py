# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
import seaborn
import tushare as ts


"""
获取单个证券的股价数据
"""
def get_single_stock_data(stock, start_date, end_date):
    # 获取证券的股价。数据类型为 pandas.core.frame.DataFrame
    data = ts.get_k_data(stock, start=start_date, end=end_date)
    # 1- 将数据 date 列指定为索引
    data.set_index('date', inplace=True)
    # 将字符串格式的 date 转换为日期格式
    data.index = pd.to_datetime(data.index)
    return data

def get_single_stock_data(stock, data_type, start_date, end_date):
    """

    :param stock:
    :param data_type:
    :param start_date:
    :param end_date:
    :return:
    """
    # 获取证券的股价。数据类型为 pandas.core.frame.DataFrame
    data = ts.get_k_data(stock, start=start_date, end=end_date)
    # 1- 将数据 date 列指定为索引
    data.set_index('date', inplace=True)
    # 将字符串格式的 date 转换为日期格式
    data.index = pd.to_datetime(data.index)
    return data

"""
获取多只证券的股价信息
"""
def get_multi_stock_data(stocks, start_date, end_date):
    datas = map(get_single_stock_data, stocks, fill_list(start_date, len(stocks)), fill_list(end_date, len(stocks)))
    return pd.concat(datas, keys=stocks, names=['Ticker', 'Date'])


"""
填充指定长度的 list
"""
def fill_list(thing, length):
    result = []
    for i in range(length):
        result.append(thing)
    return result

