# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
import tushare as ts
import talib as ta
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from aqf.com.xiumei.utils import tushare_util
# 确保‘-’号显示正常
mpl.rcParams['axes.unicode_minus']=False
# 确保中文显示正常
mpl.rcParams['font.sans-serif'] = ['SimHei']


"""
技术分析 SMA+CCI 双指标交易系统
交易信号转换为持仓信号使用循环法
"""


def sma_cci_mixed_strategy():
    """
    sma cci 双指标交易系统
    :return:
    """
    # 1- 数据获取
    data = tushare_util.get_single_stock_data('hs300', '2016-01-01', '2017-06-30')
    # 计算指标 sma，cci
    data['sma'] = ta.SMA(np.asarray(data['close']), 5)
    data['cci'] = ta.CCI(np.asarray(data['high']), np.asarray(data['low']), np.asarray(data['close']), timeperiod=20)
    # # 画图
    plt.subplot(2, 1, 1)
    plt.title('沪深300 sma cci 指标图')
    # 不显示横坐标
    plt.gca().axes.get_xaxis().set_visible(False)
    data['close'].plot(figsize=(10, 8))
    data['sma'].plot(figsize=(10, 8))
    plt.legend()
    plt.subplot(2, 1, 2)
    data['cci'].plot(figsize=(10, 8))
    plt.legend()
    plt.show()

    # 2- 交易信号、持仓信号和策略逻辑
    # 2.1- 交易信号
    # 产生开仓信号应使用昨日及前日数据，避免未来函数
    data['yes_close'] = data['close'].shift(1)
    data['yes_sma'] = data['sma'].shift(1)
    data['yes_cci'] = data['cci'].shift(1)  # CCI是作为策略的一个过滤器；
    data['daybeforeyes_close'] = data['close'].shift(2)
    data['daybeforeyes_sma'] = data['sma'].shift(2)

    # 产生交易信号
    # sma 开多信号：昨日股价上穿 SMA
    data['sma_signal'] = np.where(np.logical_and(data['daybeforeyes_close'] < data['daybeforeyes_sma'],
                                                 data['yes_close'] > data['yes_sma']), 1, 0)
    # sma开空信号：昨天股价下穿SMA
    data['sma_signal'] = np.where(np.logical_and(data['daybeforeyes_close'] > data['daybeforeyes_sma'],
                                                 data['yes_close'] < data['yes_sma']), 1, 0)
    # 产生cci做多过滤信号
    data['cci_filter'] = np.where(data['yes_cci'] < -100, 1, 0)
    # 产生cci做空过滤信号
    data['cci_filter'] = np.where(data['yes_cci'] > 100, -1, data['cci_filter'])
    # 过滤后的开多信号
    data['filtered_signal'] = np.where(data['sma_signal'] + data['cci_filter'] == 2, 1, 0)
    # 过滤后的开空信号
    data['filtered_signal'] = np.where(data['sma_signal']+data['cci_filter'] == -2, -1, data['filtered_signal'])

    # 2.2- 持仓信号
    # 记录持仓情况，默认为0
    position = 0
    # 对每一交易日进行循环
    for i, item in data.iterrows():
        # 判断交易信号
        if item['filtered_signal'] == 1:
            # 交易信号为1，则记录仓位为1
            position = 1
        elif item['filtered_signal'] == -1:
            # 交易信号为-1， 则记录仓位为-1
            position = -1
        else:
            pass
        # 记录每日持仓情况
        data.loc[i, 'position'] = position
    
    # 画图
    # plt.subplot(3, 1, 1)
    # plt.title('600030 CCI持仓图')
    # plt.gca().axes.get_xaxis().set_visible(False)
    # data['close'].plot(figsize=(12, 12))
    # plt.legend()
    # plt.subplot(3, 1, 2)
    # data['cci'].plot(figsize=(12, 12))
    # plt.legend()
    # plt.gca().axes.get_xaxis().set_visible(False)
    # plt.subplot(3, 1, 3)
    # data['position'].plot(marker='o', figsize=(12, 12), linestyle='')
    # plt.legend()
    # plt.show()
    
    # 3- 策略收益和数据可视化
    # 计算策略收益
    # 计算股票每日收益率
    data['pct_change'] = data['close'].pct_change()
    # 计算策略每日收益率
    data['strategy_return'] = data['pct_change'] * data['position']
    # 计算股票累积收益率
    data['return'] = (data['pct_change'] + 1).cumprod()
    # 计算策略累积收益率
    data['strategy_cum_return'] = (1 + data['strategy_return']).cumprod()


if __name__ == '__main__':
    sma_cci_mixed_strategy()
