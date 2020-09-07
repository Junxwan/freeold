# -- coding: utf-8 --
import os
import tkinter as tk
import numpy as np
import mplfinance as mpf
import matplotlib.ticker as mticks
from stock import data
from mplfinance._styledata import charles

# 均線顏色
MA_COLOR = ['#FF8000', '#00CCCC', '#00CC66', '#FFFF00', '#6600CC', '#CC00CC']

# 均線寬度
MA_LINE_WIDTH = 1.8

# 繪圖上文字size
PLOT_TEXT_FONT_SIZE = 15

# label style
LABEL_STYLE = {'fontsize': PLOT_TEXT_FONT_SIZE, 'rotation': 0}

# 數據-價格文字size
PRICE_LABEL_FONT_SIZE = 16

# 數據-均線文字size
MA_LABEL_FONT_SIZE = 15

# 資料欄位x軸
DATA_X = -11


class Watch():
    data_w = 1.5

    data_label = ['d', 'o', 'c', 'h', 'l']

    volume_label_name = 'v'

    def __init__(self, master, config=None, **kwargs):
        self._master = master
        self._fig = None
        self._axs = None

        self._main_ax = None
        self._volume_ax = None

        self._date_fmt = '%Y-%m-%d'
        self.data = data.Watch(os.path.join(config['data'], 'csv'), **kwargs)

        self.y_tick = 0
        self.data_y = 0

    def plot(self, code, width=100, height=100, volume=True, **kwargs):
        data = self.data.code(code, **kwargs)

        self._fig, self._axs = mpf.plot(
            data,
            type='candle',
            style=self._get_style(),
            datetime_format=self._date_fmt,
            ylabel='',
            ylabel_lower='',
            figsize=(width / 100, height / 100),
            update_width_config=self._update_width_config(),
            scale_padding=self._scale_padding(),
            volume=volume,
            returnfig=True,
            panel_ratios=(4, 1)
        )

        self._main_ax = self._axs[0]

        if volume:
            self._volume_ax = self._axs[2]
            self.data_label.append(self.volume_label_name)

        self._major(data)
        self._plot_ma(data)
        self._plot_max_min(data)
        self._plot_price_text(data)
        self._update_label()

        return self._fig

    # 繪製均線
    def _plot_ma(self, watch):
        xLen = watch.len()
        l = self.data_label.__len__()

        for i, ma in enumerate(watch.mas()):
            self._main_ax.plot(xLen, ma['data'], linewidth=MA_LINE_WIDTH, color=MA_COLOR[i])
            self._plot_data_text(i + l, f"{ma['ma']}m", fontsize=MA_LABEL_FONT_SIZE, color=MA_COLOR[i])

    # 繪製最高價與最低價
    def _plot_max_min(self, watch):
        xOffset = {
            1: 1.35,
            2: 1.35,
            3: 1.35,
            4: 1.05,
            5: 1.35,
            6: 1.35,
            7: 1.45,
        }

        self._main_ax.annotate(
            watch.y_max,
            xy=(watch.x_max, watch.y_max),
            xytext=(watch.x_max - xOffset[len(str(watch.y_max))], watch.y_max + self.y_tick / 2),
            color='white',
            size=PLOT_TEXT_FONT_SIZE,
            arrowprops=dict(arrowstyle="simple")
        )

        self._main_ax.annotate(
            watch.y_min,
            xy=(watch.x_min, watch.y_min),
            xytext=(watch.x_min - xOffset[len(str(watch.x_min))], watch.y_min - self.y_tick / 1.5),
            color='white',
            size=PLOT_TEXT_FONT_SIZE,
            arrowprops=dict(arrowstyle="simple")
        )

    # 繪製數據文字
    def _plot_price_text(self, watch):
        for i, n in enumerate(self.data_label):
            self._plot_data_text(i, n, fontsize=PRICE_LABEL_FONT_SIZE, color='white')

    def _plot_data_text(self, i, name, **kwargs):
        self._main_ax.text(
            DATA_X,
            self.data_y - (self.y_tick * ((i + 1) * self.data_w)),
            f'{name}:',
            **kwargs
        )

    # 更新label
    def _update_label(self):
        for l in self._main_ax.get_yticklabels():
            l.update(LABEL_STYLE)

        for l in self._main_ax.get_xticklabels():
            l.update(LABEL_STYLE)

        for l in self._volume_ax.get_yticklabels():
            l.update(LABEL_STYLE)

        for l in self._volume_ax.get_xticklabels():
            l.update(LABEL_STYLE)

    # 設定資料呈現邏輯與格式
    def _major(self, watch):
        self._date_locator = DateLocator(watch.data.index)
        self._date_formatter = DateFormatter()

        self._main_ax.xaxis.set_major_locator(self._date_locator)
        self._main_ax.xaxis.set_major_formatter(self._date_formatter)

        self._price_formatter = PriceFormatter()
        self._price_locator = PriceLocator(watch.y_max, watch.y_min)

        self._main_ax.yaxis.set_major_locator(self._price_locator)
        self._main_ax.yaxis.set_major_formatter(self._price_formatter)

        self.y_tick = self._price_locator.tick
        self.data_y = self._price_locator.get_ticks()[-1]

        if self._volume_ax != None:
            volume = lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (
                    x * 1e-3) if x >= 1e3 else '%1.0f' % x

            self._volume_locator = VolumeLocator(watch.volume())

            self._volume_ax.yaxis.set_major_locator(self._volume_locator)
            self._volume_ax.yaxis.set_major_formatter(mticks.FuncFormatter(volume))

    # 看盤樣式
    def _get_style(self):
        default = {
            'up': '#9A0000',
            'down': '#FFFFFF'
        }

        edge = {
            'up': '#FF0000',
            'down': '#FFFFFF'
        }

        volume = {
            'up': '#9A0000',
            'down': '#23B100'
        }

        style = charles.style

        # 蠟燭顏色
        style['marketcolors']['candle'] = default
        style['marketcolors']['edge'] = edge
        style['marketcolors']['wick'] = default
        style['marketcolors']['ohlc'] = default
        style['marketcolors']['volume'] = volume

        # 格子線
        style['gridstyle'] = '-'

        # 格子內顏色
        style['facecolor'] = '#0f0f10'
        style['base_mpl_style'] = 'dark_background'

        return style

    # 更新默認樣式寬度
    def _update_width_config(self):
        return {
            'volume_width': 0.85
        }

    # 看盤比例
    def _scale_padding(self):
        return {
            'left': 0.6,
            'right': 0.55,
            'bottom': 0.3,
        }


# 日期塞選
class DateLocator(mticks.Locator):
    def __init__(self, data):
        self._data = data
        self.locs = []

    def __call__(self):
        if len(self.locs) > 0:
            return self.locs
        return self.tick_values(None, None)

    def tick_values(self, vmin, vmax):
        monthFirstWorkDay = {}

        for i, d in enumerate(self._data):
            if d.month not in monthFirstWorkDay:
                monthFirstWorkDay[d.month] = i

        self.locs = list(monthFirstWorkDay.values())

        return self.locs


# 股價塞選
class PriceLocator(mticks.Locator):
    _tick_level = [50, 25, 10, 7.5, 5, 2.5, 1, 0.5, 0.25, 0.1, 0.05]

    def __init__(self, max, min):
        self._max = max
        self._min = min
        self.ticks = []

        diff = max - min
        self.tick = self._tick_level[0]

        for i, t in enumerate(self._tick_level):
            d = (diff / t)
            if d > 10:
                self.tick = t
                break

    def __call__(self):
        return self.tick_values(None, None)

    def get_ticks(self):
        return self.tick_values(None, None)

    def tick_values(self, vmin, vmax):
        if len(self.ticks) > 0:
            return self.ticks

        start = self._min - (self._min % self.tick)

        for i in range(20):
            p = start + (self.tick * i)
            self.ticks.append(start + (self.tick * i))

            if p > self._max:
                self.ticks.insert(0, start - self.tick)
                self.ticks.append(p + self.tick)
                break

        self.axis.set_view_interval(self.ticks[0], self.ticks[-1])

        return np.asarray(self.ticks)


# 交易量塞選
class VolumeLocator(mticks.Locator):
    def __init__(self, data):
        self._data = data

    def __call__(self):
        return self.tick_values(None, None)

    def tick_values(self, vmin, vmax):
        if len(self.locs) > 0:
            return self.locs

        max = self._data.max()
        min = self._data.min()
        step = 10 ** (len(str(int((max - min) / 3))) - 1)
        diff = (max - min) / 3
        step = int((diff - diff % step) + step)

        self.locs = [step * i for i in range(5)]

        return self.locs


# 日期格式
class DateFormatter(mticks.Formatter):
    def __call__(self, x, pos=0):
        if x < 0:
            return ''
        return self.axis.major.locator._data[x].strftime('%Y-%m-%d')

    def getTicks(self):
        if len(self.locs) == 0:
            self.locs = self.axis.major.locator.locs

        return [self.__call__(x, 0) for x in self.locs]


# 股價格式
class PriceFormatter(mticks.Formatter):
    def __call__(self, x, pos=None):
        if pos == 0:
            return ''

        return '%1.2f' % x


# 事件
class MoveEvent(tk.Frame):
    def __init__(self, canvas, data, yt=0, yMax=0):
        tk.Frame.__init__(self)

        self._data = data
        self.canvas = canvas
        self._yMax = yMax
        self._yt = yt

        self.moveEvent = self.canvas.mpl_connect('motion_notify_event', self.move)
        self.clickEvent = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.releaseEvent = self.canvas.mpl_connect('button_release_event', self.on_release)

        self.ax = canvas.figure.axes[0]
        self.axv = canvas.figure.axes[2]

        self._xv = None
        self._xh = None
        self._yv = None

        self._style = dict(fontsize=18, color='white')
        self._isPress = False

        self.init_text()

    def draw(self, event):
        x = round(event.xdata)
        date = self._data.index[x]
        p = self._data.loc[date]
        date = date.strftime('%Y-%m-%d')

        if self._xv == None:
            self._xv = self.ax.axvline(x=x, color='#FFFF00', linewidth=0.5)
            self._xh = self.ax.axhline(y=(p['close']), color='#FFFF00', linewidth=0.5)
            self._yv = self.axv.axvline(x=x, color='#FFFF00', linewidth=0.5)
        else:
            self._xv.set_xdata(x)
            self._xh.set_ydata(p['close'])
            self._yv.set_xdata(x)

            self.set_text(date, p)

        self.canvas.draw_idle()

    def set_text(self, date, price):
        self._date.set_text(date)
        self._open.set_text(price['open'])
        self._close.set_text(price['close'])
        self._high.set_text(price['high'])
        self._low.set_text(price['low'])
        self._volume.set_text(price['volume'])
        self._5ma.set_text(price['5ma'])
        self._10ma.set_text(price['10ma'])
        self._20ma.set_text(price['20ma'])

    def init_text(self):
        date = self._data.index[-1]
        price = self._data.loc[date]

        self._date = self.ax.text(-9.5, self._yMax, date.strftime('%Y-%m-%d'), fontsize=13, color='white')
        self._open = self.ax.text(-9.5, self._yMax - self._yt * 1.5, price['open'], self._style)
        self._close = self.ax.text(-9.5, self._yMax - self._yt * 3, price['close'], self._style)
        self._high = self.ax.text(-9.5, self._yMax - self._yt * 4.5, price['high'], self._style)
        self._low = self.ax.text(-9.5, self._yMax - self._yt * 6, price['low'], self._style)
        self._volume = self.ax.text(-9.5, self._yMax - self._yt * 7.5, int(price['volume']), self._style)
        self._5ma = self.ax.text(-8.5, self._yMax - self._yt * 9, int(price['5ma']), self._style)
        self._10ma = self.ax.text(-8.5, self._yMax - self._yt * 10.5, int(price['10ma']), self._style)
        self._20ma = self.ax.text(-8.5, self._yMax - self._yt * 12, int(price['20ma']), self._style)

    def on_press(self, event):
        self._isPress = True
        self.draw(event)

    def on_release(self, event):
        self._isPress = False

    def move(self, event):
        if self._isPress:
            self.draw(event)
