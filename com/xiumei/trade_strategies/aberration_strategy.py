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
Abberation 趋势跟踪股票版
"""


def aberration_strategy():
    """
    Abberation 趋势跟踪股票版
    :return:
    """
    # 1- 数据获取
    code = '002397'
    start_date = '2012-01-01'
    end_date = '2017-01-01'
    length = 10  # 参考周期长度，用于确定计算标准差及移动平均的周期
    open_trigger = 0.5  # 价格向上偏离均线0.5倍观察期内标准差的最大值开仓；
    stopwin_trigger = 3  # 价格向上偏离均线3倍观察期内标准差的最大值止盈；
    stoplose_trigger = 1  # 移动止损；跌破均值移动止损；固定止损：开仓价向下偏离观察期内标准差的最大值；
    data = tushare_util.get_single_stock_data(code, start_date, end_date).reset_index()

    # 2- 策略数据处理
    data['pct_change'] = data['close'].pct_change()
    data['ma'] = data['close'].rolling(window=length, min_periods=3).mean()
    data['std'] = data['close'].rolling(window=length, min_periods=3).mean()
    data['yes_ma'] = data['ma'].shift(1)
    # 以观察期内标准差最大值作为标准差限制指标
    data['std_limit'] = data['std'].rolling(window=length).max() # 观察期内标准差最大值
    data['yes_std_limit'] = data['std_limit'].shift(1)
    # 计算当日开仓价和止盈价
    data['long_open_price'] = data['yes_ma'] + data['yes_std_limit'] * open_trigger # 计算每一天满足条件的开仓价
    data['long_stopwin_price'] = data['yes_ma'] + data['yes_std_limit'] * stopwin_trigger # 计算每一天满足条件的止盈价
    # 计算开仓、止盈信号
    data['long_open_signal'] = np.where(data['high'] > data['long_open_price'], 1, 0)
    data['long_stopwin_signal'] = np.where(data['high'] > data['long_stopwin_price'], 1, 0)

    # 3- 策略逻辑
    # 当天有持仓，满足平仓进行平仓后，当天不开仓
    # 当天无持仓，满足开仓条件则进行开仓。开仓当日如果同时满足平仓条件，以第二日开盘价平仓
    # 记录持仓情况，0代表空仓，1代表持仓
    flag = 0

    # 前12个数据因均值计算无效不作为待处理数据；
    # 终止数据选择倒数第二个以防止当天止盈利情况会以第二天开盘价平仓导致无数据情况发生；
    # 最后一天不进行操作；可能会面临最后一天开仓之后当天触发平仓，要用到下一天开盘价卖出，无法得到。
    for i in range(12, (len(data) - 1)):
        # 有持仓进行平仓
        if flag == 1:
            # 计算止损价格，取均线和开仓价下移一定倍数标准差，两者的最大值作为止损价
            stoplose_price = max(data.loc[i, 'yes_ma'], long_open_price - long_open_delta * stoplose_trigger)
            # 多头止盈，并计算当日收益率
            if data.loc[i, 'long_stopwin_signal']:
                data.loc[i, 'return'] = data.loc[i, 'long_stopwin_price'] / data.loc[i-1, 'close'] - 1
                flag = 0
            # 多头移动止损，并计算当日收益率
            elif data.loc[i, 'low'] < stoplose_price:
                # 考虑到若当日开盘价低于止损价，无法止损的情况
                # 谨慎起见，在计算收益时，取止损价和开盘价的最小值
                data.loc[i, 'return'] = min(data.loc[i, 'open'], stoplose_price) / data.loc[i-1, 'close'] - 1
                flag = 0
            # 计算多头收益率
            else:
                data.loc[i, 'return'] = data.loc[i, 'close'] / data.loc[i-1, 'close'] -1

        # 无持仓进行开仓
        else:
            if data.loc[i, 'long_open_signal']:
                # 开仓时标记 flag = 1
                flag = 1
                # 需比较当天的开盘价和开仓价，当开盘价高于开仓价时，只能以开盘价进行平仓，不能用开仓价
                # 否则会导致策略收益高估
                # 记录开仓价
                long_open_price = max(data.loc[i, 'open'], data.loc[i, 'long_open_price'])
                # 记录开仓时的10天内的标准差的最大值；是为了计算固定止损的价格；
                long_open_delta = data.loc[i, 'yes_std_limit']
                # 记录当天盈利情况
                data.loc[i, 'return'] = data.loc[i, 'close'] / long_open_price - 1
                # 计算止损价：多头移动止损，以均线和开仓价减一定倍数标准差，两者的最大值作为止损点
                stoplose_price = max(data.loc[i, 'yes_ma'], long_open_price - long_open_delta * stoplose_trigger)
                # 如果开仓当天同时满足平仓条件，则以第二天开盘价平仓（这里做了一定的近似处理）
                if (data.loc[i, 'low'] < stoplose_price  # 满足止损条件
                        or data.loc[i, 'long_stopwin_signal']):  # 满足止盈条件
                    # 记录此次操作盈利情况并将收益记录在开仓日
                    data.loc[i, 'return'] = data.loc[i + 1, 'open'] / long_open_price - 1
                    flag = 0

    print(data.tail())
    # 4- 计算策略收益并可视化
    data['return'].fillna(0, inplace=True)
    data['strategy_return'] = (data['return'] + 1).cumprod()
    data['stock_return'] = (data['pct_change'] + 1).cumprod()
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(data.stock_return)
    ax.plot(data.strategy_return)
    plt.title(code)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    aberration_strategy()
