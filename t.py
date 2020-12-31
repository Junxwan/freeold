import json
import math
import os
import glob
import time
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import codecs
import tkinter as tk
from bs4 import BeautifulSoup
import requests
import scipy.ndimage
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
import tkinter
from xlsx import trend
from stock import data, name, weak
from ui import pattern
from scipy.interpolate import UnivariateSpline
from tkinter import ttk
from matplotlib.lines import Line2D
from pywinauto.application import Application
import pyautogui
import mplfinance as mpf
from ui import k

d = []
stock = data.Stock("D:\\data\\csv\\stock")
trend = data.Trend("D:\\data\\csv")

# paths = glob.glob(
#     os.path.join('D:\\data\\csv\\strategy\\weak\\yesterday_red_trend_high10_low11_left_head', '*', '*.csv'))
#
# for path in sorted(paths, reverse=True):
#     date = os.path.basename(path).split('.')[0]
#
#     for i, v in pd.read_csv(path).iterrows():
#         d.append([
#             v['code'],
#             v['name'],
#             date,
#             v['increase'],
#             v['d_increase'],
#             v['increase[1]'],
#             v['d_increase[1]'],
#             v['max_time'],
#             v['max_min_diff'],
#             v['volume'],
#             v['volume[1]'],
#             v['volume[2]'],
#             v['y_volume%'],
#             v['y_volume[1]%'],
#             v['5vma[1]'],
#             v['10vma[1]'],
#             v['20vma[1]'],
#             v['60vma[1]'],
#             v['5vma[1]%'],
#             v['10vma[1]%'],
#             v['20vma[1]%'],
#             v['60vma[1]%'],
#         ])
#
# pd.DataFrame(d, columns=[
#     'code', 'name', 'date', 'increase', 'd_increase', 'increase[1]', 'd_increase[1]', 'max_time', 'max_min_diff', 'volume',
#     'volume[1]',
#     'volume[2]', 'y_volume%', 'y_volume[1]%', '5vma[1]', '10vma[1]', '20vma[1]', '60vma[1]', '5vma[1]%', '10vma[1]%',
#     '20vma[1]%', '60vma[1]%',
# ]).to_csv('D:\\data\\csv\\strategy\\weak\\yesterday_red_trend_high10_low11_left_head\\r.csv', encoding='utf-8-sig',
#           index=False)

# ==========================================

# vt = [
#     15, 10, 8, 6, 5, 4, 4, 3.7, 3.5, 3.3, 3.1, 2.9
# ]
#
# execl = pd.read_excel('D:\\data\\csv\\strategy\\weak\\yesterday_red_trend_high10_low11_left_head\\1.xlsx')
#
# for i, raws in execl.iterrows():
#     vv = []
#     date = raws['date'].__str__()[:10]
#     t = trend.code(raws['code'], date)
#
#     for i, ts in enumerate(pd.date_range(start=f'{date} 09:05:00', end=f'{date} 10:00:00', freq='5min')):
#         q = t.loc['time']
#         r = q[q <= ts.__str__()]
#
#         if len(r) == 0:
#             vv.append(0)
#         else:
#             vv.append(int(t.loc[name.VOLUME].astype(float)[:int(r.index[-1])].sum()) * vt[i])
#
#     print(f"{date} {raws['code']}")
#
#     d.append(raws.tolist() + vv)
#
# pd.DataFrame(d, columns=execl.columns.tolist() + [v.__str__()[10:] for v in
#                                                   pd.date_range(start='09:05:00', end='10:00:00', freq='5min')]). \
#     to_excel('D:\\data\\csv\\strategy\\weak\\yesterday_red_trend_high10_low11_left_head\\研究.xlsx',encoding='utf-8-sig',index=False)

# ================================


paths = glob.glob(
    os.path.join('D:\\data\\csv\\strategy\\weak\\trend_high0930_low11', '*', '*.csv'))

for path in sorted(paths, reverse=True):
    date = os.path.basename(path).split('.')[0]

    for i, v in pd.read_csv(path).iterrows():
        d.append([
            v['code'],
            v['name'],
            date,
            v['max_time'],
            v['max_min_diff']
        ])

pd.DataFrame(d, columns=['code', 'name', 'date', 'max_time', 'max_min_diff']).to_csv('D:\\data\\csv\\strategy\\weak\\trend_high0930_low11\\r.csv',
                                   encoding='utf-8-sig', index=False)

r = 0


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
            if round((((mc / close) - 1) * 100), 2) > 10:
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
            if round(((mc / close) - 1) * -100, 2) > 10:
                min = mc + t

            min = round(min, get_len(min))
            break

        mc = mc - t
        mc = round(mc, get_len(mc))

    return min


#
# M頭，次頭做多空
#
#           (1)          (3)
#           **           **
#           * *         * * (4)
#           *  *       *  *
#           *   *     *   *
#           *    *   *    *
#           *     * *     *
#           *      *      *
#          (0)    (2)
#
# 09:05後開始計算
#
# (1)
# 1. 當期最高價大於目前最高價
#
# (2)
# 1. 狀態是(1)
# 2. 不能是剛轉成(1)的期數
# 3. 當期最低價與目前最高價相差1-10%
#
# (3)
# 1. 狀態是(2)
# 2. 不能是剛轉成(2)的期數
# 3. 當期高點要略高於目前最低價
# 4. 當期非是剛創新高的狀態
# 5. 當前近5期平均成交量要大於前4期的近5期平均成交量，也就是當期的量比前4期量還要大，反彈要出量
# 6. 創新高前最高的近五期平均成交量 大於 當前近5期平均成交量，也就是(1)要比(3)成交量大
#
# (4)
# 1. 狀態是(3)
# 2. 不能是剛轉成(3)的期數
# 3. 時間在9:10~12:30範圍內
# 4. (1)跟(3)需間隔至少?期數
# 5. 當期收盤價格需略低於(3)的最高價(趨勢剛往下)
#
# (0)
# 1. 狀態是(2)且當日最高價與當期最低價相差大於10%漲幅(趨勢一直往下)
# 2. (2)(3)(4)跟(1)相差期數大於?某間隔數
#
# 放空點
# 1. 是狀態是(4)且上一個狀態是(3)
# 2. 當期前最大的成交量就是在左頭前(含左頭)
#
#
# _time 兩頭間距幾根(1分Bar)
def m(data, _time=30):
    # 1: 創新高 <- 製造左頭
    # 2: 創新高後拉回 <- 左頭確立
    # 3: 創新高後拉回反彈 <- 製造右頭
    # 4: 右頭開始拉回 <- 右頭確立
    flag = 0

    # flag歷史狀況
    flagH = [0]

    # 當日最高價
    _high = 0

    # 當日最低價
    _low = 0

    # 右頭高點價格
    flag3High = 0

    # 到第幾期K棒
    barCount = 0

    # 創新高前最高的近五期平均成交量
    volumeFlag1 = 0

    # 創新高且是左頭前的最高成交量
    flag1HighVolumeBar = 0

    # 左頭bar
    flag1Bar = 0

    # 左頭後拉回bar
    flag2Bar = 0

    # 左頭後反彈bar
    flag3Bar = 0

    # 次頭bar
    flag4Bar = 0

    times = data.loc[name.TIME]
    closes = data.loc[name.CLOSE]
    lows = data.loc[name.LOW]
    highs = data.loc[name.HIGH]

    for index in data:
        [_, _, close, volume, high, low, _] = data[index]
        period = int(index)

        barCount += 1

        # 09:05開始計算
        if barCount < 4:
            continue

        # 當前最高價大於之前紀錄最高價
        if high > _high:
            # 創新高狀態
            flag = 1
            flagH.insert(0, flag)
            flag1Bar = barCount
            _high = high

            # 1. 09:50後
            # 2. 記錄左頭最大量(1分)，為了判斷抓出左頭量為當日最大量
            if barCount >= 50 and volume > flag1HighVolumeBar:
                flag1HighVolumeBar = volume

        # 1. 有創新高過
        # 2. 當期K棒非創新高K棒
        # 3. 創新高後拉回1%~10%
        elif flag == 1 and barCount != flag1Bar and _high >= low * 1.01 and low * 1.1 >= _high:
            flag = 2
            flagH.insert(0, flag)
            _low = low
            flag2Bar = barCount

        # 1. 左頭拉回
        # 2. 當日最高價與當期最低價相差大於10%漲幅
        elif flag == 2 and _high > low * 1.1:
            flag = 0
            flagH.insert(0, flag)

        # 1. 創新高狀態
        # 2. 09:05後
        if flag == 1 and barCount >= 5:
            # 記錄左頭最大量(1分)，為了判斷抓出左頭量為當日最大量
            if volume > flag1HighVolumeBar:
                flag1HighVolumeBar = volume

            avgVolume = data.loc[name.VOLUME][period - 4:period + 1].mean()

            # 1. 之前有達成左頭條件但又再創高
            # 2. 近五期平均成交量 大於 現在創新高前最高的近五期平均成交量
            if (flagH[1] != 0 and flagH[1] != 1) or avgVolume > volumeFlag1:
                volumeFlag1 = avgVolume

        # 左頭拉回後
        if flag == 2:
            # 當日最低價大於當期最低價
            if _low > low:
                _low = low

                # 紀錄最低價那根的代號，因為不能讓進入flag3的那根bar與進入flag2的相同
                flag2Bar = barCount

            # 1. 當期最高價大於目前最低價*1.007(開始反彈)
            # 2. 當期非創新高拉回後的反彈點
            if high >= _low * 1.007 and barCount != flag2Bar:
                avgVolume = data.loc[name.VOLUME][period - 4:period + 1].mean()
                avgVolume1 = data.loc[name.VOLUME][period - 5:period].mean()
                avgVolume2 = data.loc[name.VOLUME][period - 6:period - 1].mean()
                avgVolume3 = data.loc[name.VOLUME][period - 7:period - 2].mean()
                avgVolume4 = data.loc[name.VOLUME][period - 8:period - 3].mean()

                # 1. 反彈要出量
                # 2. 當前近5期平均成交量要大於前4期的近5期平均成交量，也就是當期的量比前4期量還要大
                # 3. 創新高前最高的近五期平均成交量 大於 當前近5期平均成交量，也就是左頭量要比右頭量大
                if avgVolume > avgVolume1 \
                        and avgVolume > avgVolume2 \
                        and avgVolume > avgVolume3 \
                        and avgVolume > avgVolume4 \
                        and avgVolume * 1.5 <= volumeFlag1:
                    flag = 3
                    flagH.insert(0, flag)
                    flag3Bar = barCount
                    flag3High = high

        # 右頭
        if flag == 3:
            # 當期最高價大於右頭價格
            if high > flag3High:
                flag3High = high
                flag3Bar = barCount

            # 訊號接收時間9:10~12:30
            if barCount >= 10 and barCount <= 210:
                # 左頭跟右頭需間隔至少期數
                if (flag3Bar - flag1Bar) > _time:
                    continue

                # 1. 當前價格需在接近右頭最高價附近(不能超過)
                # 2. 當期非右頭確立點
                # 3. N型時，也就是右頭開始往下
                if close < flag3High * 0.995 and barCount != flag3Bar:
                    flag = 4
                    flagH.insert(0, flag)
                    flag4Bar = barCount

        # 如果各個flag期數相差超過_time，flag重置
        if (flag2Bar - flag1Bar) > _time and (flag3Bar - flag1Bar) > _time and (flag4Bar - flag1Bar) > _time:
            flag = 0
            flagH.insert(0, flag)

        # 左頭必須是到目前為止最大的成交量
        if flag == 4 and flagH[1] == 3 and data.loc[name.VOLUME][:barCount - 4].max() == flag1HighVolumeBar:
            return [
                {
                    name.TIME: datetime.fromisoformat(times[flag1Bar]).time(),
                    name.CLOSE: closes[flag1Bar],
                    name.HIGH: highs[flag1Bar],
                    name.LOW: lows[flag1Bar],
                    name.VOLUME: volumeFlag1,
                    f"{name.HIGH}_{name.VOLUME}": flag1HighVolumeBar,
                    'bar': flag1Bar,
                },
                {
                    name.TIME: datetime.fromisoformat(times[flag2Bar]).time(),
                    name.CLOSE: closes[flag2Bar],
                    name.HIGH: highs[flag2Bar],
                    name.LOW: lows[flag2Bar],
                    'bar': flag2Bar,
                },
                {
                    name.TIME: datetime.fromisoformat(times[flag3Bar]).time(),
                    name.CLOSE: closes[flag3Bar],
                    name.HIGH: highs[flag3Bar],
                    name.LOW: lows[flag3Bar],
                    'bar': flag3Bar,
                },
                {
                    name.TIME: datetime.fromisoformat(times[flag4Bar]).time(),
                    name.CLOSE: closes[flag4Bar],
                    name.HIGH: highs[flag4Bar],
                    name.LOW: lows[flag4Bar],
                    'bar': flag4Bar,
                }
            ]


trend = data.Trend("D:\\data\\csv")
stock = data.Stock("D:\\data\\csv\\stock")
query = data.Query("D:\\data\\csv", stock=stock)

_tick_level = [50, 25, 10, 7.5, 5, 2.5, 1, 0.5, 0.25, 0.1, 0.05]


def tick(y_max, y_min):
    diff = y_max - y_min
    tick = _tick_level[0]

    for i, t in enumerate(_tick_level):
        d = (diff / t)
        if d > 10:
            tick = t
            break
    return tick


def ticks(y_max, y_min):
    diff = y_max - y_min
    tick = _tick_level[0]

    for i, t in enumerate(_tick_level):
        d = (diff / t)
        if d > 10:
            tick = t
            break

    start = (y_min - (y_min % tick)) - tick
    ticks = []

    for i in range(30):
        p = start + (tick * i)
        ticks.append(start + (tick * i))

        if p > y_max:
            ticks.insert(0, start - tick)
            ticks.append(p + tick)
            break

    return ticks


#
# 左頭
#
#     * * * * * (2)
#    *         *                                    * (1)
#   *           *                                 *
#  *             *                              *
# * (3)           *                           *
#                  *                        *
#                   *                     *
#                     *                 *
#                       * * * * * * * *
#
# 1. 如果(2)高點(黑k的開盤價,紅k的收盤價)必須大於(1)收盤價
# 2. (1)必須先創低(小於黑k的收盤價,紅k的開盤價)
# 3. 創低需達到某幅度
# 4. 創低後開始反彈且達到某幅度為(2)，持續創高則更新(2)
# 5. (2)開始不繼續創高差距達幾根K棒後確認為(3)，也就是(2)必須是高點大於(3)跟(1)
# 6. (3)必須是(2)與(3)之間的最低點(黑k的收盤價,紅k的開盤價)
#
def q(code, date):
    stock.readAll()
    dates = stock.data.loc[(2330, name.DATE), :].tolist()

    flag1Bar = dates.index(date)
    data = stock.data.loc[code].dropna(axis=1)
    data.loc[name.OPEN] = data.loc[name.OPEN].astype(float)
    data.loc[name.CLOSE] = data.loc[name.CLOSE].astype(float)
    data.loc[name.VOLUME] = data.loc[name.VOLUME].astype(float)
    data.loc[name.HIGH] = data.loc[name.HIGH].astype(float)
    data.loc[name.LOW] = data.loc[name.LOW].astype(float)
    data = data.iloc[:, flag1Bar:]
    q = weak.YesterdayRedTrendHigh10Low11_LeftHead()
    q.stockQ = stock
    q.trendQ = trend

    if q.run(data.columns[0], code, data, stock.info(code)) == False:
        return []

    return [
        [q.pattern.rightBar, data.loc[name.DATE][q.pattern.rightBar]],
        [q.pattern.leftBar, data.loc[name.DATE][q.pattern.leftBar]],
        [q.pattern.leftBottomBar, data.loc[name.DATE][q.pattern.leftBottomBar]],
    ]


def q1(d):
    for date, codes in d.items():
        for code in codes:
            a = q(code, date)
            if len(a) == 0:
                return []

            draw_k(code, date, a, title='q')


#
# 股價接近左頭(相差幾%)
# 1. 有左頭
# 2. (1)與(2)相差大於幾%
#
#     * * * * * (2)
#    *         *                                    * (1)
#   *           *                                 *
#  *             *                              *
# * (3)           *                           *
#                  *                        *
#                   *                     *
#                     *                 *
#                       * * * * * * * *
#
def g(code, date):
    stock.read('202001')
    stock.read('2019')
    dates = stock.data.loc[(2330, name.DATE), :].tolist()

    flag1Bar = dates.index(date)
    data = stock.data.loc[code].dropna(axis=1)
    data.loc[name.OPEN] = data.loc[name.OPEN].astype(float)
    data.loc[name.CLOSE] = data.loc[name.CLOSE].astype(float)
    data.loc[name.VOLUME] = data.loc[name.VOLUME].astype(float)
    data.loc[name.HIGH] = data.loc[name.HIGH].astype(float)
    data.loc[name.LOW] = data.loc[name.LOW].astype(float)
    data = data.iloc[:, flag1Bar:]
    q = weak.YesterdayRedDIncrease1_5_LeftHeadNearRight()

    if q.run(data.columns[0], code, data, None, stock.info(code)) == False:
        return []

    return [
        [q.pattern.rightBar, data.loc[name.DATE][q.pattern.rightBar]],
        [q.pattern.leftBar, data.loc[name.DATE][q.pattern.leftBar]],
        [q.pattern.leftBottomBar, data.loc[name.DATE][q.pattern.leftBottomBar]],
    ]


def g1(d):
    for date, codes in d.items():
        for code in codes:
            a = g(code, date)
            if len(a) == 0:
                return []

            draw_k(code, date, a, title='g')


#
# 股價今日突破左頭
# 1. 有左頭
# 2. 今天收盤價大於(2)收盤價
#                                                       * (1)
#     * * * * * (2)                                   *
#    *         *                                    *
#   *           *                                 *
#  *             *                              *
# * (3)           *                           *
#                  *                        *
#                   *                     *
#                     *                 *
#                       * * * * * * * *
#
def e(code, date):
    stock.read('202001')
    stock.read('2019')
    dates = stock.data.loc[(2330, name.DATE), :].tolist()

    flag1Bar = dates.index(date)
    data = stock.data.loc[code].dropna(axis=1)
    data.loc[name.OPEN] = data.loc[name.OPEN].astype(float)
    data.loc[name.CLOSE] = data.loc[name.CLOSE].astype(float)
    data.loc[name.VOLUME] = data.loc[name.VOLUME].astype(float)
    data.loc[name.HIGH] = data.loc[name.HIGH].astype(float)
    data.loc[name.LOW] = data.loc[name.LOW].astype(float)
    data = data.iloc[:, flag1Bar:]
    q = weak.YesterdayRedDIncrease1_5_LeftHeadFirstBreakthrough()

    if q.run(data.columns[0], code, data, None, stock.info(code)) == False:
        return []

    return [
        [q.pattern.rightBar, data.loc[name.DATE][q.pattern.rightBar]],
        [q.pattern.leftBar, data.loc[name.DATE][q.pattern.leftBar]],
        [q.pattern.leftBottomBar, data.loc[name.DATE][q.pattern.leftBottomBar]],
    ]


def e1(d):
    for date, codes in d.items():
        for code in codes:
            a = e(code, date)
            if len(a) == 0:
                return []

            draw_k(code, date, a, title='e')


# 下降
#
#
#  * * * * * (3)
#            *
#              *
#                *
#                  * * * * * (2)
#                           *
#                            *
#                             *
#                              * * * * * * * * (1)
#
def f(code, date):
    stock.read('202001')
    stock.read('2019')
    dates = stock.data.loc[(2330, name.DATE), :].tolist()

    flag1Bar = dates.index(date)
    data = stock.data.loc[code].dropna(axis=1)
    data.loc[name.OPEN] = data.loc[name.OPEN].astype(float)
    data.loc[name.CLOSE] = data.loc[name.CLOSE].astype(float)
    data.loc[name.VOLUME] = data.loc[name.VOLUME].astype(float)
    data.loc[name.HIGH] = data.loc[name.HIGH].astype(float)
    data.loc[name.LOW] = data.loc[name.LOW].astype(float)
    data = data.iloc[:, flag1Bar:]
    q = weak.YesterdayRedDIncrease1_5_Decline()

    if q.run(data.columns[0], code, data, None, stock.info(code)) == False:
        return []

    return [
        [q.pattern.rightBar, data.loc[name.DATE][q.pattern.rightBar]],
        [q.pattern.leftBar, data.loc[name.DATE][q.pattern.leftBar]],
    ]


def f1(d):
    for date, codes in d.items():
        for code in codes:
            a = f(code, date)
            if len(a) == 0:
                return []

            draw_k(code, date, a, title='f')


# 平台
def r(code, date):
    stock.read('202001')
    stock.read('2019')
    dates = stock.data.loc[(2330, name.DATE), :].tolist()

    flag1Bar = dates.index(date)
    data = stock.data.loc[code].dropna(axis=1)
    data.loc[name.OPEN] = data.loc[name.OPEN].astype(float)
    data.loc[name.CLOSE] = data.loc[name.CLOSE].astype(float)
    data.loc[name.VOLUME] = data.loc[name.VOLUME].astype(float)
    data.loc[name.HIGH] = data.loc[name.HIGH].astype(float)
    data.loc[name.LOW] = data.loc[name.LOW].astype(float)
    data = data.iloc[:, flag1Bar:]
    q = weak.YesterdayRedDIncrease1_5_Platform()

    if q.run(data.columns[0], code, data, None, stock.info(code)) == False:
        return []

    return [
        [q.pattern.rightBar, data.loc[name.DATE][q.pattern.rightBar]],
        [q.pattern.leftBar, data.loc[name.DATE][q.pattern.leftBar]],
    ]


def r1(d):
    for date, codes in d.items():
        for code in codes:
            a = r(code, date)
            if len(a) == 0:
                return []

            draw_k(code, date, a, title='r', h=True)


def draw_k(code, date, a, title='', h=False):
    if len(a) == 0:
        return

    d = stock.data.loc[code]
    ds = stock.data.loc[2330].loc[name.DATE].tolist()
    ds.index(date)

    d = d.iloc[:, ds.index(date):90 + ds.index(date)].dropna(axis=1)
    ds = d.loc[name.DATE].tolist()

    if a[-1][0] > d.columns[-1]:
        return

    n = np.full(d.shape[1], np.nan)

    dsd = d.loc[name.DATE].tolist()

    for v in a:
        n[dsd.index(v[1])] = d.loc[name.CLOSE][v[0]] * 0.99

    apd = mpf.make_addplot(n[::-1], type='scatter', markersize=100, marker='^')

    dd = pd.DataFrame(
        {
            name.DATE: pd.to_datetime(d.loc[name.DATE].iloc[::-1]).tolist(),
            name.OPEN: d.loc[name.OPEN].iloc[::-1].tolist(),
            name.CLOSE: d.loc[name.CLOSE].iloc[::-1].tolist(),
            name.HIGH: d.loc[name.HIGH].iloc[::-1].tolist(),
            name.LOW: d.loc[name.LOW].iloc[::-1].tolist(),
            name.VOLUME: d.loc[name.VOLUME].iloc[::-1].tolist(),
        }
    )

    fig, axlist = mpf.plot(dd.set_index(name.DATE), type='candle', addplot=apd, ylabel=f"{code} {date} {title}",
                           returnfig=True)

    if h:
        ds = d.loc[name.DATE].tolist()
        y = d.iloc[:, ds.index(a[0][1]): ds.index(a[1][1]) + 1]

        c = y.loc[name.CLOSE]
        o = y.loc[name.OPEN]

        if c.max() > o.max():
            axlist[0].axhline(y=c.max())
        else:
            axlist[0].axhline(y=o.max())

        if c.min() > o.min():
            axlist[0].axhline(y=c.min())
        else:
            axlist[0].axhline(y=o.min())

    fig.set_tight_layout(False)

    for ax in axlist:
        ax.yaxis.set_major_locator(k.PriceLocator(dd[name.HIGH].max(), dd[name.LOW].min()))
        ax.yaxis.set_major_formatter(k.PriceFormatter())
        ax.xaxis.set_major_locator(k.DateLocator(ds))
        ax.xaxis.set_major_formatter(k.DateFormatter())

    mpf.show()


# 股價接近左頭(相差幾%)
# 股價第一次突破左頭
# 下降
# 平台
# 左頭
def hh(code, date):
    v = {
        date: [code],
    }

    g1(v)
    e1(v)
    f1(v)
    r1(v)
    q1(v)


# g1(3376, '2020-01-02')
# e1(3372, '2020-01-02')
# f1(1313, '2020-01-03')
# q1(6426, '2020-01-02')
# r1(6426, '2020-01-02')
# hh(8341, '2020-01-31')

# 股價接近左頭(相差幾%)
g1({
    '2020-01-31': [
        # 4746, 1907
    ],
    '2020-01-30': [
        # 6452, 4167, 1590, 2387, 2474, 4714
    ],
    '2020-01-17': [
        # 3413, 6451, 6166, 2456, 4744, 3217, 2474
    ],
    '2020-01-16': [
        # 5328, 6411
    ],
    '2020-01-15': [
        # 6234, 6127, 2456, 4968
    ],
    '2020-01-14': [
        # 4967, 3413, 3035, 6139, 3680
    ],
    '2020-01-13': [
        # 3624, 3545
    ],
    '2020-01-10': [
        # 3680, 3680, 2478, 3374, 3527, 3041, 6239, 5457, 8034
    ],
    '2020-01-09': [
        # 9802, 3515, 6173
    ],
    '2020-01-08': [
        # 6261
    ],
    '2020-01-07': [
        # 9802, 3530, 6446, 3227, 3413, 9938
    ],
    '2020-01-03': [
        # 4953, 4935, 2379, 3016, 4973, 4977, 4967,
        # 3588, 6121, 6125, 2449, 6414, 4953
    ],
    '2020-01-02': [
        # 3083, 8155
    ],
})

# 股價今日突破左頭
e1({
    '2020-01-31': [
        # 6582, 1720, 4746, 4121, 8341
    ],
    '2020-01-30': [
        # 8059
    ],
    '2020-01-18': [
        # 3489, 6165, 6121
    ],
    '2020-01-17': [
        # 6451, 3218, 3530, 6166, 3661, 2369, 5483, 5521, 6271
    ],
    '2020-01-16': [
        # 3515, 6411, 1732
    ],
    '2020-01-15': [
        # 6266, 5347
    ],
    '2020-01-14': [
        # 4550, 3376, 8210, 2427
    ],
    '2020-01-10': [
        # 3094, 3227, 3406, 2368
    ],
    '2020-01-08': [
        # 3594
    ],
    '2020-01-07': [
        # 6175, 4979, 6446, 9955, 6288
    ],
    '2020-01-06': [
        # 8390
    ],
    '2020-01-03': [
        # 6488, 6284, 6269, 3105, 3376,
        # 2345, 6166, 3035, 2489, 3105
    ],
    '2020-01-02': [
        # 8155
    ],
})

# 下降
f1({
    '2020-01-31': [
        # 6582, 1907
    ],
    '2020-01-30': [
        # 6452, 3406, 1590, 4714
    ],
    '2020-01-16': [
        # 1732, 9919
    ],
    '2020-01-15': [
        # 6510, 2492, 2456, 2455, 2327, 3026
    ],
    '2020-01-14': [
        # 2461, 6139
    ],
    '2020-01-13': [
        # 3546, 1589, 1789
    ],
    '2020-01-10': [
        # 3374, 3041, 6239, 2338, 1519, 5457, 8034, 8150
    ],
    '2020-01-09': [
        # 6271
    ],
    '2020-01-07': [
        # 6288,
    ],
    '2020-01-03': [
        # 3588, 3413, 6121, 8088, 8046, 2489, 6414
    ],
    '2020-01-02': [
        # 6612
    ],
})

# 平台
r1({
    '2020-01-31': [
        # 6582, 1720, 2108, 8341
    ],
    '2020-01-30': [
        # 3653, 3698, 8182
    ],
    '2020-01-18': [
        # 3489, 6165, 8088
    ],
    '2020-01-17': [
        # 4744
    ],
    '2020-01-16': [
        # 4908, 4161, 6411
    ],
    '2020-01-15': [
        # 6234, 6531, 5347
    ],
    '2020-01-14': [
        # 4967, 3413, 6251
    ],
    '2020-01-10': [
        # 6531, 3374, 3041, 3227
    ],
    '2020-01-09': [
        # 8271
    ],
    '2020-01-07': [
        # 8040
    ],
    '2020-01-06': [
        # 1313, 1305
    ],
    '2020-01-03': [
        # 2415, 4968, 4953, 4977, 3044,
        # 8081, 2489, 3372, 4953
    ],
})

# 左頭
q1({
    '2020-10-19': [2201],
})
