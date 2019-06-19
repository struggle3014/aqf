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
布林带策略：
该策略中交易信号转持仓信号采用循环法

"""


def bbands_strategy():
    """
    布林带策略
    :return:
    """
    # 1- 数据准备
    data = tushare_util.get_single_stock_data('hs300', '2016-01-01', '2017-07-01')
    # 计算 bolling 线
    data['upper'], data['middle'], data['lower'] = ta.BBANDS(
        np.asarray(data['close']), timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    # 绘图
    # fig = plt.figure(figsize=(10, 6))
    # plt.title('沪深300 布林线图')
    # plt.plot(data['close'])
    # plt.plot(data['upper'], linestyle='--')
    # plt.plot(data['middle'], linestyle='--')
    # plt.plot(data['lower'], linestyle='--')
    # plt.legend()
    # plt.show()

    # 2- 交易信号和持仓信号计算（分开计算）
    # 计算昨日数据
    data['yes_close'] = data['close'].shift(1)
    data['yes_lower'] = data['lower'].shift(1)
    data['yes_upper'] = data['upper'].shift(1)
    # 计算前天数据
    data['daybeforeyes_close'] = data['close'].shift(2)
    data['daybeforeyes_lower'] = data['lower'].shift(2)
    data['daybeforeyes_upper'] = data['upper'].shift(2)

    # 计算交易信号
    # 开多信号：前天收盘价低于下轨，昨日收盘价高于下轨
    data['signal'] = np.where(np.logical_and(data['daybeforeyes_close'] < data['daybeforeyes_lower'],
                                             data['yes_close'] > data['yes_lower']), 1, 0)
    # 开空信号：前天收盘价高于上轨，昨日收盘价低于上轨
    data['signal'] = np.where(np.logical_and(data['daybeforeyes_close'] > data['daybeforeyes_upper'],
                                             data['yes_close'] < data['yes_upper']), -1, data['signal'])

    # 绘制交易信号图
    # plt.subplot(2, 1, 1)
    # plt.title('沪深300 bolling交易信号图')
    # plt.gca().axes.get_xaxis().set_visible(False)
    # data['close'].plot(figsize=(10, 10))
    # plt.plot(data['upper'], linestyle='--')
    # plt.plot(data['middle'], linestyle='--')
    # plt.plot(data['lower'], linestyle='--')
    # plt.legend()
    # plt.subplot(2, 1, 2)
    # plt.plot(data['signal'], marker='o', linestyle='')
    # plt.legend()
    # plt.show()

    # 使用position标记持仓情况，全新的循环法思路；
    position = 0
    # 对每个交易日进行循环    
    for item in data.iterrows():  # 逐行遍历；返回的这个item其实一个元组，（label，series）
        # 判断交易信号
        if item[1]['signal'] == 1:
            # 交易信号为1，则记录仓位为1，持有多仓；
            position = 1
        elif item[1]['signal'] == -1:
            # 交易信号为-1， 则记录仓位为-1，持有空仓；
            position = -1
        else:
            pass  # 啥都不做；
        # 记录每日持仓情况
        data.loc[item[0], 'position'] = position  # 自动往下填充的就是上一个产生的交易信号；关键；

    # # 使用position标记持仓情况，全新的循环法思路；另外一种方法；
    # position = 0
    # # 对每个交易日进行循环
    # for i, item in data.iterrows():  # 逐行遍历；这里item就是一个Series； unpacked
    #     # 判断交易信号
    #     if item['signal'] == 1:
    #         # 交易信号为1，则记录仓位为1，持有多仓；
    #         position = 1
    #     elif item['signal'] == -1:
    #         # 交易信号为-1， 则记录仓位为-1，持有空仓；
    #         position = -1
    #     else:
    #         pass
    #     # 记录每日持仓情况
    #     data.loc[i, 'position'] = position  # 在DataFrame中自动往下填充的就是上一个产生的交易信号；关键；

    # 绘制持仓情况图
    # plt.subplot(2, 1, 1)
    # plt.gca().axes.get_xaxis().set_visible(False)
    # data['close'].plot(figsize=(10, 8))
    # plt.plot(data['upper'], linestyle='--')
    # plt.plot(data['middle'], linestyle='--')
    # plt.plot(data['lower'], linestyle='--')
    # plt.legend()
    # plt.subplot(2, 1, 2)
    # plt.plot(data['position'], marker='o', linestyle='')
    # plt.legend()
    # plt.suptitle('沪深300 bolling持仓情况')
    # plt.show()

    # 3- 计算策略收益及可视化
    # 计算股票每日收益率
    data['pct_change'] = data['close'].pct_change()
    # 计算股票的累积收益率
    data['return'] = (data['pct_change'] + 1).cumprod()
    # 计算策略每日收益率
    data['strategy_return'] = data['position'] * data['pct_change']
    # 计算策略累积收益率
    data['cum_strategy_return'] = (data['strategy_return'] + 1).cumprod()

    # 绘图
    fig = plt.figure(figsize=(10, 6))
    plt.plot(data['return'])
    plt.plot(data['cum_strategy_return'])
    plt.title('沪深300 收益曲线图')
    plt.legend(loc='upper left')
    plt.show()


if __name__ == '__main__':
    bbands_strategy()