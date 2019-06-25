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
基于 K 线锤子线的趋势跟踪策略
"""


def hammer_strategy():
    """
    基于 K 线锤子线的趋势跟踪策略
    :return:
    """
    code = '002398'  # 股票代码
    start_date = '2012-01-01' # 开始时间
    end_date = '2017-01-01' # 结束时间
    body_size = 0.03  # 表示锤子实体大小上限，基准为当日开盘价，实体不能太大，波动范围限制在3%；
    head_size = 0.5  # 表示锤子上影线长度上限，基准为下影线长度，上影线要短一点，不能超过下影线的的一半；
    tail_size = 2  # 表示下影线与实体大小比值，下影线要大于实体两倍；
    length = 10  # 表示观察期时间长短；
    stoplose_trigger = 1  # 表示当价格偏离均线满足几倍标准差时止损

    # 1- 收集并计算所需数据
    data = tushare_util.get_single_stock_data(code, start_date, end_date)
    data.reset_index(inplace=True)
    data['pct_change'] = data['close'].pct_change()
    data['ma'] = data['close'].rolling(length).mean()
    data['std'] = data['close'].rolling(length).std()
    # 计算昨天的 mean 和昨天的 std
    data['yes_ma'] = data['ma'].shift(1)
    data['yes_std'] = data['std'].shift(1)

    # 2- 识别锤子形态
    # 计算实体、上影线、下影线
    data['body'] = abs(data['open'] - data['close']) # 计算 K 线实体
    data['head'] = data['high'] - data[['open', 'close']].max(axis=1) # 计算上影线，按行计算
    data['tail'] = data[['open', 'close']].min(axis=1) - data['low'] # 计算下影线

    # 判断 K 线各部分是否符合锤子要求
    data['body_cond'] = np.where(data['body'] / data['open'] < body_size, 1, 0) # 实体的大小比开盘要小于 3%,K 线实体不能太大
    data['head_cond'] = np.where(data['tail'] == 0, False,
                                 data['head'] / data['tail'] < head_size)  # 上影线不能比下影线的一半长
    data['tail_cond'] = np.where(data['body'] == 0, True,
                                 (data['tail'] / data['body']) > tail_size)  # 下影线要比实体的两倍更长才满足条件

    print(data.tail(15)[['date', 'head', 'body', 'open', 'tail', 'body_cond', 'head_cond', 'tail_cond']])

    # 判断 K 线是否符合锤子线
    data['hammer'] = data[['head_cond', 'body_cond', 'tail_cond']].all(axis=1) # 同时满足上述三个条件才是锤子 K 线
    # 由于实盘当天中的日线级别参考指标未生成，因根据昨日是否满足锤子形态要求作为开仓信号
    data['yes_hammer'] = data['hammer'].shift(1)

    print(data[data['hammer']][['date', 'hammer']].tail(15))

    # print(data[data['hammer']].tail(10))

    # 3- 编写交易逻辑——循环法
    flag = 0  # 持仓记录，1代码有仓位，0代表空仓；
    for i in range(2 * length, len(data)): # 从20天开始计算，因为前期数据无效；
        # 如果已持仓，判断是否止损
        if flag == 1:
            stoplose_price = max(data.loc[i, 'yes_ma'] - stoplose_trigger * data.loc[i, 'yes_std'],
                                 long_open_price - long_open_delta)
            # 当天价格低于止损价，则进行止损，一个是移动止损，一个是开仓时候的开仓和开仓价-1倍标准差；
            if data.loc[i, 'low'] < stoplose_price:  # 接下来要做的都是止损的操作；
                flag = 0
                # 计算清盘当天的收益；取min是因为，如果当天开盘价就小于了止损价，那么我们就要以开盘价就止损；
                # 不然会导致策略收益高估；
                data.loc[i, 'return'] = stoplose_price / data.loc[i - 1, 'close'] - 1
                # 如果未持仓，判断是否进行开仓
            else:
                data.loc[i, 'return'] = data.loc[i, 'close'] / data.loc[i - 1, 'close'] - 1
        else:
            # 判断是否为下降趋势，平均重心是下降的；锤子线开仓要满足形态和下降趋势；
            if data.loc[i - length, 'yes_ma'] > data.loc[i, 'yes_ma']:
                # 判断是否符合锤子形态
                if data.loc[i, 'yes_hammer']:
                    # 更改持仓标记
                    flag = 1
                    # 记录开仓时开仓价格及标准差:是为了做固定止损；
                    long_open_price = data.loc[i, 'open']
                    long_open_delta = data.loc[i, 'yes_std']
                    # 计算当天收益率
                    data.loc[i, 'return'] = data.loc[i, 'close'] / data.loc[i, 'open'] - 1  # 以产生信号之后的第二天开盘价开仓；
                    # data.loc[i, 'trade_mark'] = 10  # 表示当天开仓
                    # 当天开仓之后不进行平仓判断

    # 4- 计算策略收益率
    data['return'].fillna(0, inplace=True)  # 对大循环中未处理的：既没有持仓，也不满足开仓条件的日期进行处理，则让这些天的return都等于0；
    data['strategy_return'] = (data['return'] + 1).cumprod()
    data['stock_return'] = (data['pct_change'] + 1).cumprod()

    # 5- 绘图
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(data.stock_return)
    ax.plot(data.strategy_return)
    plt.title(code)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    hammer_strategy()
