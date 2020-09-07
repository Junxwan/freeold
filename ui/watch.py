# -- coding: utf-8 --

import os
import tkinter as tk
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticks
from stock import data
from mplfinance._styledata import charles
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 均線顏色
MA_COLOR = ['#FF8000', '#00CCCC', '#00CC66', '#FFFF00', '#6600CC', '#CC00CC']

# 技術線寬度
LINE_WIDTH = 1.8

# 座標size
XY_TEXT_FONT_SIZE = 24

# label style
LABEL_STYLE = {'fontsize': XY_TEXT_FONT_SIZE, 'rotation': 0}

# 數據框-價格文字size
PRICE_LABEL_FONT_SIZE = 25

# 數據-均線文字size
MA_LABEL_FONT_SIZE = 30

# 數據框-價格名稱style
PRICE_NAME_STYLE = dict(fontsize=PRICE_LABEL_FONT_SIZE, color='white')

# 數據框-價格數據style
PRICE_VALUE_STYLE = dict(fontsize=PRICE_LABEL_FONT_SIZE, color='white')

# 資料欄位x軸
DATA_X = -11.0


class Watch():
    data_h = 1.5

    text = {
        data.DATE: {
            'name': 'd',
            'text': None,
            'style': [PRICE_NAME_STYLE, PRICE_VALUE_STYLE],
        },
        data.OPEN: {
            'name': 'o',
            'text': None,
            'style': [PRICE_NAME_STYLE, PRICE_VALUE_STYLE],
        },
        data.CLOSE: {
            'name': 'c',
            'text': None,
            'style': [PRICE_NAME_STYLE, PRICE_VALUE_STYLE],
        },
        data.HIGH: {
            'name': 'h',
            'text': None,
            'style': [PRICE_NAME_STYLE, PRICE_VALUE_STYLE],
        },
        data.LOW: {
            'name': 'l',
            'text': None,
            'style': [PRICE_NAME_STYLE, PRICE_VALUE_STYLE],
        },
    }

    volume_text = {
        'name': 'v',
        'text': None,
        'style': [PRICE_NAME_STYLE, PRICE_VALUE_STYLE],
    }

    def __init__(self, master, config=None, **kwargs):
        self._master = master
        self._fig = None
        self._axs = None
        self.canvas = None
        self.event = None

        self._main_ax = None
        self._image_ax = {}
        self._sup_ax = {}

        self._date_fmt = '%Y-%m-%d'
        self.data = data.Watch(os.path.join(config['data'], 'csv'), **kwargs)

        self.y_tick = 0
        self.data_y = 0

    def plot(self, code, width=100, height=100, volume=True, **kwargs):
        self.watch = self.data.code(code, **kwargs)

        self._fig, self._axs = mpf.plot(
            self.watch.data,
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
            self._sup_ax[data.VOLUME] = self._axs[2]
            self.text[data.VOLUME] = self.volume_text

        self._major()
        self._plot_price()
        self._plot_ma()
        self._plot_max_min()
        self._update_label()

        return self._fig

    # 繪製數據文字
    def _plot_price(self):
        i = 0
        for k, v in self.text.items():
            style = v['style']
            self._plot_data_text(i, v['name'], **style[0])
            v['text'] = self._plot_data_value_text(i, self.watch.data[k][-1], x=1, **style[1])
            i += 1

    # 繪製均線
    def _plot_ma(self):
        xLen = np.arange(self.watch.len())
        l = self.text.__len__()

        for i, ma in enumerate(self.watch.mas()):
            self._image_ax[ma['name']] = self._main_ax.plot(xLen, ma['data'], linewidth=LINE_WIDTH, color=MA_COLOR[i])

            style = [
                dict(fontsize=PRICE_LABEL_FONT_SIZE, color=MA_COLOR[i]),
                PRICE_VALUE_STYLE
            ]

            self._plot_data_text(i + l, ma['name'], **style[0])

            self.text[ma['name']] = {
                'name': ma['name'],
                'text': self._plot_data_value_text(i + l, ma['data'][-1], x=3, **style[1]),
                'style': style
            }

    # 繪製最高價與最低價
    def _plot_max_min(self):
        xOffset = {
            1: 1.35,
            2: 1,
            3: 0.9,
            4: 1.05,
            5: 1.35,
            6: 1.35,
            7: 1.45,
        }

        bbox = dict(boxstyle='square', fc="0.5")

        self._image_ax['max_bar'] = self._main_ax.annotate(
            self.watch.y_max,
            xy=(self.watch.x_max, self.watch.y_max),
            xytext=(self.watch.x_max - xOffset[len(str(self.watch.y_max))], self.watch.y_max + self.y_tick / 2),
            color='black',
            size=XY_TEXT_FONT_SIZE,
            arrowprops=dict(arrowstyle="simple"),
            bbox=bbox
        )

        self._image_ax['min_bar'] = self._main_ax.annotate(
            self.watch.y_min,
            xy=(self.watch.x_min, self.watch.y_min),
            xytext=(self.watch.x_min - xOffset[len(str(self.watch.y_min))], self.watch.y_min - self.y_tick),
            color='black',
            size=XY_TEXT_FONT_SIZE,
            arrowprops=dict(arrowstyle="simple"),
            bbox=bbox
        )

    # 繪製數據值
    def _plot_data_value_text(self, i, text, x=0, **kwargs):
        kwargs['bbox'] = dict(boxstyle='square')
        kwargs['color'] = 'black'

        return self._plot_data_text(i, text, x=x + DATA_X, **kwargs)

    # 繪製數據文字
    def _plot_data_text(self, i, text, x=DATA_X, **kwargs):
        return self._main_ax.text(
            x,
            self.data_y - (self.y_tick * ((i + 1) * self.data_h)),
            text,
            **kwargs
        )

    # 更新label
    def _update_label(self):
        for l in self._main_ax.get_yticklabels():
            l.update(LABEL_STYLE)

        for l in self._main_ax.get_xticklabels():
            l.update(LABEL_STYLE)

        for ax in self._sup_ax.values():
            for l in ax.get_yticklabels():
                l.update(LABEL_STYLE)

            for l in ax.get_xticklabels():
                l.update(LABEL_STYLE)

    # 設定資料呈現邏輯與格式
    def _major(self):
        self._date_locator = DateLocator(self.watch.data.index)
        self._date_formatter = DateFormatter()

        self._main_ax.xaxis.set_major_locator(self._date_locator)
        self._main_ax.xaxis.set_major_formatter(self._date_formatter)

        self._price_formatter = PriceFormatter()
        self._price_locator = PriceLocator(self.watch.y_max, self.watch.y_min)

        self._main_ax.yaxis.set_major_locator(self._price_locator)
        self._main_ax.yaxis.set_major_formatter(self._price_formatter)

        self.y_tick = self._price_locator.tick
        self.data_y = self._price_locator.get_ticks()[-1]

        if data.VOLUME in self._sup_ax:
            self._volume_major(self.watch.volume())

    def _volume_major(self, volume):
        fun = lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (
                x * 1e-3) if x >= 1e3 else '%1.0f' % x

        self._volume_locator = VolumeLocator(volume)

        self._sup_ax[data.VOLUME].yaxis.set_major_locator(self._volume_locator)
        self._sup_ax[data.VOLUME].yaxis.set_major_formatter(mticks.FuncFormatter(fun))

    # 即時顯示資料
    def event_show_data(self, event, d):
        for k, v in self.text.items():
            if k == data.DATE:
                p = d[k]
            else:
                p = '%1.2f' % d[k]

            v['text'].set_text(p)

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
            'bottom': 0.2,
        }

    # 設定呈現在TK
    def set_tk(self, master):
        self._main_ax.name = data.CLOSE
        axs = [self._main_ax]

        for n, v in self._sup_ax.items():
            v.name = n
            axs.append(v)

        self.canvas = FigureCanvasTkAgg(self._fig, master)
        self.event = MoveEvent(self.canvas, self.watch.data, axs)
        self.event.add_callback(self.event_show_data)
        self.canvas.draw()

    # 直接show圖
    def show(self):
        plt.show()

    # 執行
    def pack(self):
        if self.canvas != None:
            self.canvas.get_tk_widget().focus_force()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


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
                self.ticks.append(p + self.tick * 2)
                break

        self.axis.set_view_interval(self.ticks[0], self.ticks[-1])

        return np.asarray(self.ticks)


# 交易量塞選
class VolumeLocator(mticks.Locator):
    def __init__(self, data):
        self._data = data
        self.locs = []

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
    def __init__(self, canvas, data, axs):
        tk.Frame.__init__(self)

        self._data = data
        self.canvas = canvas
        self._axs = axs
        self._vax = {}
        self._hax = {}
        self._callbacks = []

        self.moveEvent = self.canvas.mpl_connect('motion_notify_event', self.move)
        self.clickEvent = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.releaseEvent = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.releaseEvent = self.canvas.mpl_connect('key_release_event', self.key_release)
        self._style = dict(color='#FFFF66', linewidth=1)
        self._isPress = False

    # 事件
    def add_callback(self, fun):
        self._callbacks.append(fun)

    # 重畫
    def draw(self, event):
        if event.xdata == None:
            return

        x = round(event.xdata)
        d = self._data.index[x]
        p = self._data.loc[d]

        if len(self._vax) == 0:
            for ax in self._axs:
                self._vax[ax.name] = ax.axvline(x=x, **self._style)
        else:
            for ax in self._vax.values():
                ax.set_visible(True)
                ax.set_xdata(x)

        if event.inaxes.name not in self._hax:
            self._hax[event.inaxes.name] = event.inaxes.axhline(y=(p[event.inaxes.name]), **self._style)

        for name, ax in self._hax.items():
            if name == event.inaxes.name:
                ax.set_visible(True)
                ax.set_ydata(p[event.inaxes.name])
            else:
                ax.set_visible(False)

        for fun in self._callbacks:
            fun(event, p)

        self.canvas.draw_idle()

    # 點擊
    def on_press(self, event):
        self._isPress = True
        self.draw(event)

    # 釋放
    def on_release(self, event):
        self._isPress = False

    # 移動
    def move(self, event):
        if self._isPress:
            self.draw(event)

    def key_release(self, event):
        if event.key == 'escape':
            for ax in self._vax.values():
                ax.set_visible(False)

            for ax in self._hax.values():
                ax.set_visible(False)

            self.canvas.draw_idle()
