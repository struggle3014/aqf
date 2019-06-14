# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import tushare as ts
from dateutil.parser import parse
from com.xiumei.utils import tushare_util

"""
金融时间序列数据处理
"""


def python_data_trans():
    """
    1.1 python 下的日期格式——Datetime 数据及转换
    :return:
    """
    now = datetime.now()  # datetime.datetime
    print('{}月{}月{}日'.format(now.year, now.month, now.day))
    print(datetime.now() - datetime(2017, 8, 19))


def time2str():
    """
    1.2 python 下时间转日期
    :return:
    """
    dt_time = datetime(2019, 6, 18)
    # 1- str(datetime.datetime)
    str_time1 = str(dt_time)
    # 2- datetime.datetime.strftime('format')
    str_time2 = dt_time.strftime('%d/%m/%Y')


def str2time():
    """
    1.3 python 字符串转换为 datetime 格式
    :return:
    """
    dt_str1 = '2019-06-08'
    # 1- datetime.strptime('str', 'format')
    dt_time1 = datetime.strptime(dt_str1, '%Y-%m-%d')
    dt_str2 = '01-06-2019'
    # 2- parse 不需要指定解析格式。
    dt_time2 = parse(dt_str2)
    print(type(dt_time2))
    print(dt_time2)


def pandas_time():
    """
    2 pandas 下的 time 使用
    2.1 timestamp: pandas 最基本的时间格式是 TimeStamp，使用 .to_datetime() 转换为 datetime。
    2.2 DatetimeIndex: pandas 下的时间索引格式。
    2.3 Period: 时期（period）指的是一段时间。
    :return:
    """
    # 1- pd.to_datetime(pandas.core.series.Series)，Series 向量化将字符串转为 datetime。
    str_time = pd.Series(['2017/06/18', '2017/06/19', '2017-06-20', '2017-06-21'], name='Course_time')
    # print(type(str_time))
    dt_time = pd.to_datetime(str_time)
    # print(dt_time)

    # 2- DatetimeIndex
    # 2.1- 使用 datetime 格式创建 DatetimeIndex
    dates1 = [datetime(2019, 8, 1), datetime(2019, 8, 2)]
    dates1 = pd.DatetimeIndex(dates1)
    # 此处需注意，python 中的 datetime 转换为 pandas(Series/DataFrame) 下的时间索引 DatetimeIndex；
    df = pd.Series(np.random.randn(2), index=dates1)
    dates2 = pd.date_range('8/1/2019', periods=10)
    df = pd.Series(np.random.randn(10), index=dates2)
    # DataFrame 使用 DatetimeIndex 可以便捷选取特定年、月、日
    # print(df['2019'])
    # print(df['2019-08'])
    # print(df['2019-08-01'])
    # print(df.index)

    # 2.2- 字符串转化为 DatetimeIndex
    date_time = pd.to_datetime(['June 18, 2017', '2016-06-19',
                                '2016.6.20', None])
    # print(date_time)

    # 3- Period
    # type 为 pandas.core.indexes.period.PeriodIndex
    time_period = pd.period_range('2017-01-01', periods=12, freq='M')
    print(type(time_period))
    # type 为 pandas.core.indexes.datetimes.DatetimeIndex
    date_range = pd.date_range('2017-01-01', periods=12, freq='M')
    print(type(date_range))
    # period对象的起始时间和终止时间
    time_period + 1
    # 创建PeriodIndex
    period_index = pd.period_range('1/1/2017', '12/31/2017', freq='M')
    # 以PeriodIndex为索引创建Series
    ps = pd.Series(np.random.randn(12), index=period_index)

    # 4- 应用
    data = ts.get_k_data('000001', '2018-01-01', '2109-06-06')
    data.index = pd.to_datetime(data['date'])
    del data['date']
    data.head()
    # 4.1- 获取 DataFrame 信息
    data.info()
    # 4.2- 切片
    data['2018-06-05':'2019-01-01']
    data['2018-01':'2018-02-12']
    data.loc['2018-01-04']
    # 在 DataFrame 下可使用 DateTimeIndex 可进行年、月进行索引。
    print(data['2018'])
    print(data['2018-02'])
    # DataFrame 不支持下列索引
    print(data['2018-02-01'])


def time_series_process():
    """
    3 时间序列数据处理
    3.1 时间数据的聚合
    3.2 时间数据的频率转换
    3.3 数据频率转换应用
    :return:
    """
    # 1- 时间序列数据前后移动
    data = tushare_util.get_single_stock_data('000001', '2018-01-01', '2019-01-01')
    close_price = data['close']
    # 获取前一天收盘价 Series(pandas.core.series.Series)
    previous_close_price = close_price.shift(1)
    # 计算收盘价百分比。两种方式：1，使用 当天收盘价/前一天收盘价 - 1 2，
    # print((close_price / previous_close_price - 1).head())
    # 计算累计收益率
    cum_return = (close_price / previous_close_price - 1).cumprod()
    # print(cum_return.head())

    # 2- 时间序列数据的频率调整
    # 2.1- 时间数据的聚合
    # 计算某月中每日收益率的平均值
    cum_return['2018-01'].mean()
    # DataFrame.resample 主要用于升采样和降采样。
    cum_return.resample('M').mean().head()
    cum_return.resample('M').ohlc().head()
    # deprecated 方法已过期
    # cum_return.resample('M', how='mean').head()

    # 2.2- 时间数据的频率转换
    sample = cum_return[1:3]
    # print(sample)
    sample_by_hour = sample.resample('H')
    # print(sample_by_hour.size())
    # print(sample_by_hour.head())

    # 2.3- 数据频率转换应用实战
    df = tushare_util.get_tick_data('600848', date='2018-12-12', src='tt')
    # df = ts.get_tick_data('600848', date='2018-12-12', src='tt')
    print(df.head(5))
    print(df.info())


if __name__ == '__main__':
    # python_data_trans()
    # time2str()
    # str2time()
    # pandas_time()
    time_series_process()
