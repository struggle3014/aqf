# -*- coding=utf-8 -*-
from aqf.com.xiumei.utils import tushare_util
import pandas as pd
import numpy as np
import tushare as ts
import talib as ta
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('seaborn')
mpl.style.use('ggplot')
# 确保‘-’号显示正常
mpl.rcParams['axes.unicode_minus']=False
# 确保中文显示正常
mpl.rcParams['font.sans-serif'] = ['SimHei']


"""
大数据舆情分析策略
"""


def popfeeling_strategy():
    """
    大数据舆情分析策略
    :return:
    """
    # 1- 数据整理
    # 1.1- 读取论文数据。论文数据作者做过 Normalize。
    paper_data = pd.read_csv('../data/paper_data.csv', sep=' ', parse_dates=True)
    data = pd.DataFrame({'Google_week': paper_data['Google End Date'],
                         'Debt': paper_data['debt'].astype(np.float64),
                         'Date': paper_data['DJIA Date'],
                         'DJClose': paper_data['DJIA Closing Price'].astype(np.float64)})
    print(data.head())
    data['Date'] = pd.to_datetime(data['Date'])
    data['Google_week'] = pd.to_datetime(data['Google_week'])
    data.reset_index().set_index('Google_week', inplace=True)

    # 1.2- 读取从谷歌搜索指数数据
    # TODO 此过程省略

    # 2- 交易信号和交易策略
    data['MA'] = data['Debt'].shift(1).rolling(window=3).mean()
    print(data.head())
    # 产生交易信号
    data['single'] = np.where(data['Debt'] > data['MA'], -1, 1)
    data.loc[:3, 'signal'] = 0
    # print(data.head())

    # 3- 计算策略收益并可视化
    data['pct_change'] = data['DJClose'].pct_change()
    data['ret'] = data['pct_change'] * data['single'].shift(1)
    # 计算累计收益率
    data['cumret'] = (1 + data['ret']).cumprod()
    print(data.tail(10))

    data['cumret'].plot(figsize=(12, 6))
    plt.show()


if __name__ == '__main__':
    popfeeling_strategy()
