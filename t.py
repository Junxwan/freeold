import os
import time
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tkinter as tk
from bs4 import BeautifulSoup
import requests
import scipy.ndimage
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
import tkinter
from stock import data, name
from ui import pattern
from scipy.interpolate import UnivariateSpline
from tkinter import ttk
from matplotlib.lines import Line2D
from pywinauto.application import Application
import pyautogui
import mplfinance as mpf


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
#
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


trend = data.Trend("C:\\Users\\hugh8\\Desktop\\research\\data\\csv")
stock = data.Stock("C:\\Users\\hugh8\\Desktop\\research\\data\\csv\\stock")


def s():
    data = trend.code(3016, '2020-10-22').dropna(axis=1)
    data.loc[name.OPEN] = data.loc[name.OPEN].astype(float)
    data.loc[name.CLOSE] = data.loc[name.CLOSE].astype(float)
    data.loc[name.VOLUME] = data.loc[name.VOLUME].astype(int)
    data.loc[name.HIGH] = data.loc[name.HIGH].astype(float)
    data.loc[name.LOW] = data.loc[name.LOW].astype(float)
    data.loc[name.AVG] = data.loc[name.AVG].astype(float)

    a = m(data)

    stock.read('202010')
    b_close = stock.yesterday(3016, '2020-10-22')[name.CLOSE]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.set_ylim(get_min(b_close), get_max(b_close))
    ax.grid(True)

    xl = np.arange(len(data.loc[name.CLOSE]))
    n = np.full(len(data.loc[name.CLOSE]), np.nan)

    f1 = n.copy()
    f1[a[0]['bar']] = a[0]['close']

    f2 = n.copy()
    f2[a[1]['bar']] = a[1]['close']

    f3 = n.copy()
    f3[a[2]['bar']] = a[2]['close']

    f4 = n.copy()
    f4[a[3]['bar']] = a[3]['close']

    ax.plot(xl, data.loc[name.CLOSE])
    ax.plot(xl, data.loc[name.HIGH], color='red')
    ax.plot(xl, data.loc[name.LOW], color='green')
    ax.plot(xl, f1, 'o', color='black')
    ax.plot(xl, f2, 'o', color='black')
    ax.plot(xl, f3, 'o', color='black')
    ax.plot(xl, f4, 'o', color='black')

    plt.show()


# U
# 3042 2020-10-29 2020-09-17
# 3083 2019-12-31 2019-11-27
def q(code, date):
    stock.read('202010')
    stock.read('202009')
    stock.read('202008')
    stock.read('202007')
    dates = stock.data.loc[(2330, name.DATE), :].tolist()
    startBar = dates.index(date)

    data = stock.data.loc[code]
    data.loc[name.OPEN] = data.loc[name.OPEN].astype(float)
    data.loc[name.CLOSE] = data.loc[name.CLOSE].astype(float)
    data.loc[name.VOLUME] = data.loc[name.VOLUME].astype(int)
    data.loc[name.HIGH] = data.loc[name.HIGH].astype(float)
    data.loc[name.LOW] = data.loc[name.LOW].astype(float)

    flag1Close = data[startBar][name.CLOSE]

    flag1Bar = 0

    for index in data:
        barIndex = index + startBar + 1
        value = data[barIndex]

        if value[name.HIGH] >= flag1Close and flag1Close >= value[name.LOW]:
            flag1Bar = barIndex
            break

    data = data.iloc[:, startBar:flag1Bar + 1]
    if (data[startBar + 1].loc[name.CLOSE] / data.loc[name.CLOSE].min()) < 1.08:
        return None

    flag2Bar = data.loc[name.CLOSE].astype(float).idxmin()

    return {
        'flag1Bar': flag1Bar,
        'flag1Date': data.loc[name.DATE][flag1Bar],
        'flag2Bar': flag2Bar,
        'flag2Date': data.loc[name.DATE][flag2Bar],
    }


def q1(code, date):
    a = q(code, date)
    d = stock.data.loc[code]
    n = np.full(60, np.nan)
    ds = stock.data.loc[2330].loc[name.DATE].tolist()
    ds.index(date)

    apd = mpf.make_addplot(n[::-1], type='scatter', markersize=100, marker='^')
    d.loc[name.DATE] = pd.to_datetime(d.loc[name.DATE].iloc[::-1])
    d = d.iloc[:, ds.index(date):60 + ds.index(date)]

    n[a['flag1Bar'] - ds.index(date)] = d.loc[name.CLOSE][a['flag1Bar']] * 0.99
    n[a['flag2Bar'] - ds.index(date)] = d.loc[name.CLOSE][a['flag2Bar']] * 0.99

    d = pd.DataFrame(
        {
            name.DATE: d.loc[name.DATE].tolist(),
            name.OPEN: d.loc[name.OPEN].iloc[::-1].tolist(),
            name.CLOSE: d.loc[name.CLOSE].iloc[::-1].tolist(),
            name.HIGH: d.loc[name.HIGH].iloc[::-1].tolist(),
            name.LOW: d.loc[name.LOW].iloc[::-1].tolist(),
            name.VOLUME: d.loc[name.VOLUME].iloc[::-1].tolist(),
        }
    )

    mpf.plot(d.set_index(name.DATE), type='candle', addplot=apd)
    mpf.show()


# 下降
# 6612 2019-12-30 2019-11-28
def f(code, date):
    stock.read('202001')
    stock.read('2019')
    dates = stock.data.loc[2330].loc[name.DATE].tolist()
    data = stock.data.loc[code].iloc[:, dates.index(date):]
    ma = data.loc[name.CLOSE].rolling(5).mean().round(2).dropna()

    if data.loc[name.OPEN].max() > data.loc[name.CLOSE].max():
        flag1Bar = data.loc[name.OPEN].astype(float).idxmax()
    else:
        flag1Bar = data.loc[name.CLOSE].astype(float).idxmax()

    flag = 0
    flag2Bar = 0
    d = ma[:flag1Bar - dates.index(date) + 1][::-1]
    s = d[d.index[0] - d.idxmax():]

    for index, value in s.items():
        if s.index[-1] != index:
            isH = value >= s[index - 1]
        else:
            isH = False

        if flag == 0 and isH:
            flag = 1
        if flag == 1 and isH == False:
            flag = 2
        elif flag == 2 and value > s[index + 4]:
            flag2Bar = 0
            break

        flag2Bar = index - 4

    return {
        'flag1Bar': flag1Bar,
        'flag1Date': data[flag1Bar][name.DATE],
        'flag2Bar': flag2Bar,
        'flag2Date': data[flag2Bar][name.DATE],
    }


def f1(code, date):
    a = f(code, date)
    d = stock.data.loc[code]
    n = np.full(60, np.nan)
    ds = stock.data.loc[2330].loc[name.DATE].tolist()
    ds.index(date)

    apd = mpf.make_addplot(n[::-1], type='scatter', markersize=100, marker='^')
    d.loc[name.DATE] = pd.to_datetime(d.loc[name.DATE].iloc[::-1])
    d = d.iloc[:, ds.index(date):60 + ds.index(date)]

    n[a['flag1Bar'] - ds.index(date)] = d.loc[name.CLOSE][a['flag1Bar']] * 0.99
    n[a['flag2Bar'] - ds.index(date)] = d.loc[name.CLOSE][a['flag2Bar']] * 0.99

    d = pd.DataFrame(
        {
            name.DATE: d.loc[name.DATE].tolist(),
            name.OPEN: d.loc[name.OPEN].iloc[::-1].tolist(),
            name.CLOSE: d.loc[name.CLOSE].iloc[::-1].tolist(),
            name.HIGH: d.loc[name.HIGH].iloc[::-1].tolist(),
            name.LOW: d.loc[name.LOW].iloc[::-1].tolist(),
            name.VOLUME: d.loc[name.VOLUME].iloc[::-1].tolist(),
        }
    )

    mpf.plot(d.set_index(name.DATE), type='candle', addplot=apd)
    mpf.show()


# q1(3042, '2020-10-29')
f1(6612, '2019-12-30')
