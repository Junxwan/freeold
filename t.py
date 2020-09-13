import math

from stock import data, builder
from xlsx import cmoney
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf

# d = data.Stock('C:\\Users\\hugh8\\Desktop\\research\\data\\csv\\stock')
# d.read('202009')
# d.read('202008')
# d.read('202007')
# d.yesterday(2330, '2020-09-04')
close = 149.5


# 股價tick
def get_tick(close):
    if close >= 1000:
        return 5
    elif close >= 500:
        return 1
    elif close >= 100:
        return 0.5
    elif close >= 50:
        return 0.1
    elif close >= 10:
        return 0.05
    else:
        return 0.01


# 股價區間內小數點
def get_len(close):
    if close < 50:
        return 2
    elif close < 500:
        return 1

    return 0


# 漲停價
def get_max(close):
    # 漲停價為昨日收盤價上漲10%
    max = round(close * 1.1, get_len(close))
    mc = close

    # 由於漲幅會受到股價不同區間而tick不同，
    # 所以在計算股價時如果有跨區間時tick不同會造成計算漲幅超過10%
    # 如昨日收盤價51.2，跌停為46.1，漲停為56.3，但tick跨越0.05跟0.1
    # 到了50元股價就不能用0.05來計算否則會超過10%限制
    while True:
        t = get_tick(mc)

        if max <= mc:
            if ((mc / close) - 1) * 100 > 10:
                max = mc - t

            max = round(max, get_len(max))
            break

        mc = mc + t
        mc = round(mc, get_len(mc))

    return max


# 跌停價
def get_min(close):
    # 跌停價為昨日收盤價下跌10%
    min = round(close * 0.9, get_len(close))
    mc = close

    # 由於漲幅會受到股價不同區間而tick不同，
    # 所以在計算股價時如果有跨區間時tick不同會造成計算漲幅超過10%
    # 如昨日收盤價51.2，跌停為46.1，漲停為56.3，但tick跨越0.05跟0.1
    # 到了50元股價就不能用0.05來計算否則會超過10%限制
    while True:
        t = get_tick(mc)

        if min >= mc:
            if ((mc / close) - 1) * -100 > 10:
                min = mc + t

            min = round(min, get_len(min))
            break

        mc = mc - t
        mc = round(mc, get_len(mc))

    return min


f_len = get_len(close)
tick = get_tick(close)
max = get_max(close)
min = get_min(close)
list = []

# 當走勢y軸每個間隔都可以一直時就直接以此間隔做y軸計算
# 1. 漲停與跌停價不能跨tick
# 2. 第二低跌停股價與其他y軸價格差異需一致
# 如昨日收盤31.9 漲停35.05 跌停28.75，此時每一個y軸價格間距為1.05
t = round((close - min) / 3, f_len)
if (get_tick(min) == get_tick(max)) & (round(t % tick, f_len) == tick):
    [list.append(round(min + (i * t), f_len)) for i in range(6)]
else:
    # 由於y軸間價格間距無法計算出統一差異，所以定義除了第二低跌停股價差異跟其他價格不同
    # 如昨日收盤17.6 跌停15.85 漲停19.35，第二跌停價為16.25，所以16.25 - 15.85 = 0.4
    # 第三跌停價之後為16.7/17.15/17.6，17.15 - 16.7 = 0.45，之後y軸都是0.45價格差異
    list.append(min)

    t = get_tick(close)
    num = round((close - min) / t) / 4
    yt = math.ceil(num) * t

    [list.append(round(close - (yt * i), f_len)) for i in sorted(range(4), reverse=True)]
    [list.append(round(close + (yt * (i + 1)), f_len)) for i in range(3)]

list.append(max)

pass
