# -- coding: utf-8 --

import os
import tkinter as tk
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticks
from stock import data
from datetime import datetime
from mplfinance._styledata import charles
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Watch():
    xy_data_style = {'fontsize': 30, 'rotation': 0}

    main_panel = 0

    def __init__(self, master, config=None, **kwargs):
        self._master = master
        self._fig = None
        self._axs = None
        self.canvas = None
        self.event = None

        self.text = None
        self.sub = {}

        self.watch = data.Watch(os.path.join(config['data'], 'csv'), **kwargs)

        self.y_tick = 0
        self.y_max_tick = 0

    def plot(self, code, width=100, height=100, date=None, **kwargs):
        self.data = self.watch.code(code, date=date)

        self._fig, self._axs = mpf.plot(
            self.data.get(),
            type='candle',
            style=self._get_style(),
            datetime_format='%Y-%m-%d',
            ylabel='',
            ylabel_lower='',
            figsize=(width / 100, height / 100),
            update_width_config=self._update_width_config(),
            scale_padding=self._scale_padding(),
            volume=kwargs.get('volume'),
            returnfig=True,
            panel_ratios=(4, 1)
        )

        self._axs[0].name = data.CLOSE
        self._axs[2].name = data.VOLUME

        self._major()

        self.text = DataLabel(
            self._main_axes(),
            self.data,
            m_min=-11,
            y_max=self.y_max_tick,
            y_tick=self.y_tick,
        )

        kwargs['index'] = -1

        self.load_sub(self._main_axes(), {
            'ma': MA(),
            'max_min': MaxMin(),
        }, **kwargs)

        self.load_sub(self._axs[2], {
            'volume': Volume(),
        }, **kwargs)

        self._update_label()

        return self._fig

    # 設定資料呈現邏輯與格式
    def _major(self):
        main = self._main_axes()
        main.xaxis.set_major_locator(DateLocator(self.data.date()))
        main.xaxis.set_major_formatter(DateFormatter())

        (y_max, y_min) = self.data.get_y_max_min()
        price_locator = PriceLocator(y_max, y_min)

        main.yaxis.set_major_locator(price_locator)
        main.yaxis.set_major_formatter(PriceFormatter())

        self.y_tick = price_locator.tick
        self.y_max_tick = price_locator.get_ticks()[-1]

    def _main_axes(self):
        return self._axs[self.main_panel]

    def load_sub(self, axes, objects, **kwargs):
        keys = kwargs.keys()

        for name, object in objects.items():
            if name in keys:
                object.set_axes(axes)
                object.plot(self._fig, self.data, **kwargs)
                object.plot_text(self.text, self.data, **kwargs)
                self.sub[name] = object

    # 更新label
    def _update_label(self):
        for ax in [self._main_axes(), self._axs[2]]:
            for l in ax.get_yticklabels():
                l.update(self.xy_data_style)

            for l in ax.get_xticklabels():
                l.update(self.xy_data_style)

    # 即時顯示資料
    def event_show_data(self, event, d):
        self.text.update(d)

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
        self.canvas = FigureCanvasTkAgg(self._fig, master)
        self.event = MoveEvent(self.canvas, self.data, [self._axs[0], self._axs[2]])
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


# 即時數據
class DataLabel():
    title_font_size = 30
    value_font_size = 25

    text = {
        'd': data.DATE,
        'o': data.OPEN,
        'c': data.CLOSE,
        'h': data.HIGH,
        'l': data.LOW,
        'v': data.VOLUME,
    }

    def __init__(self, axes, data, m_min=0, y_max=0, y_tick=0):
        self._axes = axes
        self._data = data

        self._title = {}
        self._value = {}

        self._m_min = m_min
        self._y_max = y_max
        self._y_tick = y_tick

        for n, c in self.text.items():
            self.add(n, c, self._data.get(column=c)[-1], offset_x=1.5)

    def add(self, name, key, value, color='white', offset_x=1.0):
        self.set_title(name, key, color=color)
        self.set_value(key, value, offset_x=offset_x)

    def set_title(self, name, key, color='white'):
        i = len(self._title)
        self._title[key] = self._axes.text(
            self._m_min,
            self._y_max - (self._y_tick * ((i + 1) * 2)),
            name,
            fontsize=self.title_font_size, color=color,
        )

    def set_value(self, name, value, color='black', offset_x=0.0):
        if name not in self._title:
            return

        title = self._title[name]

        self._value[name] = self._axes.text(
            title._x + offset_x,
            title._y,
            value,
            fontsize=self.value_font_size, color=color, bbox=dict(boxstyle='square'),
        )

    def remove(self, name):
        if name in self._title:
            self._title[name].remove()
            self._value[name].remove()

            del self._title[name]
            del self._value[name]

    def update(self, value):
        for name, ax in self._value.items():
            if name == data.DATE:
                p = value[name]
            else:
                p = '%1.2f' % value[name]

            ax.set_text(p)


class SubAxes():
    def __init__(self):
        self._line = {}

    def set_axes(self, axes):
        self._axes = axes

    def plot(self, figure, data, **kwargs):
        pass

    def plot_text(self, text, data, **kwargs):
        pass

    def remove(self, **kwargs):
        pass


# 均線
class MA(SubAxes):
    # 顏色
    color = {
        5: '#FF8000',
        10: '#00CCCC',
        20: '#00CC66',
        60: '#FFFF00',
        120: '#6600CC',
        240: '#CC00CC',
    }

    line_width = 1.8

    def __init__(self):
        SubAxes.__init__(self)

    def plot(self, figure, data, **kwargs):
        ma = kwargs.get('ma')

        if ma == None:
            return

        data = data.get_ma(ma)

        for d in ma:
            if d not in self._line:
                self._add(d, data[f'{d}ma'])

        day = {d: '' for d in ma}

        for d, v in self._line.items():
            if d not in day:
                v.remove()
                del self._line[d]

    def plot_text(self, text, data, **kwargs):
        index = kwargs.get('index')
        for name, line in self._line.items():
            key = f'{name}ma'
            text.add(key, key, self._line[name][0]._y[index], color=self.color[name], offset_x=3.5)

    def _add(self, day, data):
        if day in self.color:
            color = self.color[day]
        else:
            color = 'red'

        line = self._axes.plot(
            np.arange(len(data)),
            data,
            linewidth=self.line_width,
            color=color,
        )

        self._line[day] = line

        return line

    def remove(self, **kwargs):
        name = kwargs.get('name')
        if name in self._line[name]:
            self._line[name].remove()
            del self._line[name]


# 最高價與最低價
class MaxMin(SubAxes):
    offset_x = {
        1: 1.35,
        2: 1,
        3: 0.9,
        4: 1.05,
        5: 1.35,
        6: 1.35,
        7: 1.45,
    }

    def __init__(self):
        SubAxes.__init__(self)
        self._max = None
        self._min = None

    def plot(self, figure, data, **kwargs):
        y_tick = self._axes.yaxis.major.locator.tick
        (x_max, y_max) = data.get_xy_max()
        (x_min, y_min) = data.get_xy_min()

        self._set(x_max, y_max, y_offset=(y_tick / 2))
        self._set(x_min, y_min, y_offset=-y_tick)

    def _set(self, x, y, y_offset=0.0):
        self._axes.annotate(
            y,
            xy=(x, y),
            xytext=(x - self.offset_x[len(str(y))], y + y_offset),
            color='black',
            size=30,
            arrowprops=dict(arrowstyle="simple"),
            bbox=dict(boxstyle='square', fc="0.5")
        )

    def remove(self, **kwargs):
        if self._max != None:
            self._max.remove()

        if self._min != None:
            self._min.remove()


# 成交量
class Volume(SubAxes):
    def plot(self, figure, data, **kwargs):
        self._major(data.volume())

    def _major(self, data):
        fun = lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (
                x * 1e-3) if x >= 1e3 else '%1.0f' % x

        self._axes.yaxis.set_major_locator(VolumeLocator(data))
        self._axes.yaxis.set_major_formatter(mticks.FuncFormatter(fun))

    def remove(self, **kwargs):
        self._axes.remove()


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
        p = self._data.index(x)

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

        if event.key == 'enter':
            # self.canvas.figure.axes[0].collections[0].remove()
            # self.canvas.figure.axes[0].collections[0].remove()
            # self.canvas.figure.axes[0].lines[0].remove()
            # self.canvas.figure.axes[0].set_yticks([290,310,330,350,370,390,410,430,450,470,490])
            self.canvas.draw_idle()


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
            d = datetime.fromisoformat(d)
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
        return self.axis.major.locator._data[x]

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
