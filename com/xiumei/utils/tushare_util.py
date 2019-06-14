# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
import seaborn
import tushare as ts


def get_single_stock_data(stock, start_date, end_date):
    """
    获取单个证券的股价数据
    :param stock:
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


def get_multi_stock_data(stocks, start_date, end_date):
    """
    获取多只证券的股价信息
    :param stocks:
    :param start_date:
    :param end_date:
    :return:
    """
    datas = map(get_single_stock_data, stocks, fill_list(start_date, len(stocks)), fill_list(end_date, len(stocks)))
    return pd.concat(datas, keys=stocks, names=['Ticker', 'Date'])


def get_tick_data(code=None, date=None, retry_count=3, pause=0.001, src='sn'):
    """
    获取指定 code 的分笔（tick）数据
    :param code: 股票代码
    :param date: 日期，yyyy-MM-dd 格式
    :param retry_count: 重试次数
    :param pause: 默认 0,重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
    :param src: 数据源选择，可输入sn(新浪)、tt(腾讯)、nt(网易)，默认sn
    :return:
    ---------
    DataFrame 当日所有股票交易数据(DataFrame)
              属性:成交时间、成交价格、价格变动，成交手、成交金额(元)，买卖类型
    """
    data = ts.get_tick_data(code, date, retry_count, pause, src)
    data.set_index('time', inplace=True)
    data.index = pd.to_datetime(data.index)
    return data


def fill_list(thing, length):
    """
    填充指定长度的 list
    :param thing:
    :param length:
    :return:
    """
    result = []
    for i in range(length):
        result.append(thing)
    return result


if __name__ == "__main__":
    print()


