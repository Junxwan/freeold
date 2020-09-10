# -- coding: utf-8 --

import os
import tkinter as tk
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticks
import mplfinance._utils as mutils
import mplfinance._widths as mwidths
import mplfinance.plotting as mplotting
from stock import data
from datetime import datetime
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Watch():
    xy_data_style = {'fontsize': 28, 'rotation': 0}

    main_panel = 0

    def __init__(self, master, config=None, **kwargs):
        self._master = master
        self._fig = None
        self._axes = {}
        self.canvas = None
        self.event = None
        self.text = None
        self.watch = data.Watch(os.path.join(config['data'], 'csv'), **kwargs)

        self._use_style()

    # 繪製
    def plot(self, code, width=100, height=100, date=None, **kwargs):

        # self._fig, self._axs = mpf.plot(
        #     self._c_watch.get(),
        #     type='candle',
        #     datetime_format='%Y-%m-%d',
        #     ylabel='',
        #     ylabel_lower='',
        #     figsize=(width / 100, height / 100),
        #     returnfig=True,
        #     panel_ratios=(4, 1)
        # )

        self.kwargs = kwargs
        self._fig, axes_list = self._figure(width, height, (4, 1))
        self._c_watch = self.watch.code(code, date=date)

        i = 0
        for name, object in self._master_axse().items():
            object.draw(code, axes_list[i], self.text, self._c_watch, self.watch, **kwargs)
            self._axes[name] = object
            i += 1

        return self._fig

    # 繪製某個股
    def plot_code(self, code, date=None):
        c_watch = self.watch.code(code, date=date)
        if c_watch == None:
            return False

        self.event.clear()
        self.event.set_data(c_watch)
        self.canvas.draw_idle()

        return True

    # 繪製畫板
    def _figure(self, width, height, panel_ratios):
        fig = plt.figure()
        fig.set_size_inches((width / 100, height / 100))

        left_pad = 0.108
        right_pad = 0.055
        top_pad = 0.12
        bot_pad = 0.036
        plot_height = 1.0 - (bot_pad + top_pad)
        plot_width = 1.0 - (left_pad + right_pad)

        hs = pd.DataFrame({'height': []})
        psum = sum(panel_ratios)
        for panid, size in enumerate(panel_ratios):
            hs.at[panid, 'height'] = plot_height * size / psum

        axes = []
        for index, row in hs.iterrows():
            lift = hs['height'].loc[(index + 1):].sum()

            if index == 0:
                ax = fig.add_axes([left_pad, bot_pad + lift, plot_width, row.height])
            else:
                ax = fig.add_axes([left_pad, bot_pad + lift, plot_width, row.height], sharex=axes[0])

            ax.set_axisbelow(True)
            axes.append(ax)

        return fig, axes

    # 主圖清單
    def _master_axse(self):
        return {
            'k': K(),
            data.VOLUME: Volume(),
        }

    # 即時顯示資料
    def event_show_data(self, event, d):
        self.text.update(d)

    # 設定看盤樣式
    def _use_style(self):
        plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']
        plt.rcParams['axes.unicode_minus'] = False

        plt.style.use('dark_background')
        plt.rcParams.update([
            ('axes.edgecolor', 'white'),
            ('axes.linewidth', 1.5),
            ('axes.labelsize', 'large'),
            ('axes.labelweight', 'semibold'),
            ('axes.grid', True),
            ('axes.grid.axis', 'y'),
            ('grid.linewidth', 0.4),
            ('lines.linewidth', 2.0),
            ('font.weight', 'medium'),
            ('font.size', 10.0),
        ])

        plt.rcParams.update({
            'axes.facecolor': '#0f0f10',
            'grid.linestyle': '-',
            'grid.color': '#a0a0a0',
        })

    # 設定呈現在TK
    def set_tk(self, master):
        self.canvas = FigureCanvasTkAgg(self._fig, master)

        self.event = MoveEvent(self.canvas, self._c_watch, self._axes.values())
        self.event.add_callback(self.event_show_data)
        self.canvas.draw()

    # 直接show圖
    def show(self):
        plt.show()

    def clear(self):
        self._fig.remove()

    # 執行
    def pack(self):
        if self.canvas != None:
            self.canvas.get_tk_widget().focus_force()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


# 即時數據
class DataLabel():
    title_font_size = 28
    value_font_size = 28

    def __init__(self, axes, x_min=0):
        self._axes = axes

        self._title = {}
        self._value = {}

        self._x_min = x_min
        self._y_max = axes.yaxis.major.locator.get_ticks()[-1]
        self._y_tick = axes.yaxis.major.locator.tick

    def add(self, name, key, value, color='white', offset_x=1.0):
        self.set_title(name, key, color=color)
        self.set_value(key, value, offset_x=offset_x)

    def set_title(self, name, key, color='white'):
        i = len(self._title)
        self._title[key] = self._axes.text(
            self._x_min,
            self._y_max - (self._y_tick * ((i + 1) * 1.2)),
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

    def clear(self):
        for v in self._title.values():
            v.remove()
        for v in self._value.values():
            v.remove()

        self._title.clear()
        self._value.clear()

    def update(self, value):
        for name, ax in self._value.items():
            if name == data.DATE:
                p = value[name]
            else:
                p = '%1.2f' % value[name]

            ax.set_text(p)


class SubAxes():
    xy_data_style = {'fontsize': 28, 'rotation': 0}

    def __init__(self):
        self._sup = {}
        self._line = {}

    def draw(self, code, axes, text, c_watch, watch, **kwargs):
        self.code = code
        self._axes = axes
        self._c_watch = c_watch
        self._watch = watch

        self._plot(**kwargs)
        # self._plot_text(text, **kwargs)
        self._load_sup(text, **kwargs)

    def _plot(self, **kwargs):
        pass

    def _plot_text(self, text, **kwargs):
        pass

    def _load_sup(self, text, **kwargs):
        for name, object in self._sup_axes().items():
            object.draw(self.code, self._axes, text, self._c_watch, self._watch, **kwargs)
            self._sup[name] = object

    def _sup_axes(self):
        return {}

    # 更新label
    def _update_label(self):
        self._axes.yaxis.set_tick_params(which='major', labelleft=False, labelright=True)

        for l in self._axes.get_yticklabels():
            l.update(self.xy_data_style)

        for l in self._axes.get_xticklabels():
            l.update(self.xy_data_style)

    def clear(self):
        pass

    def remove(self, **kwargs):
        pass


# K線
class K(SubAxes):
    text = {
        '日': data.DATE,
        '開': data.OPEN,
        '收': data.CLOSE,
        '高': data.HIGH,
        '低': data.LOW,
    }

    def __init__(self):
        SubAxes.__init__(self)
        self.info = None

    # 繪製主圖
    def _plot(self, **kwargs):
        self._axes.name = data.CLOSE
        y_max, y_min = self._c_watch.get_y_max_min()
        self._axes.set_xlim(-0.5, self._c_watch.range - 0.5)
        self._axes.set_ylim(y_min, y_max)

        self._plot_k()
        self._update_label()

    # 繪製文案
    def _plot_text(self, text, **kwargs):
        info = self._watch.info(self.code)

        if info.on == 1:
            on = '上市'
        else:
            on = '上櫃'

        _y_tick = self._axes.yaxis.major.locator.tick
        _y_max = self._axes.yaxis.major.locator.get_ticks()[-1]

        self.info = self._axes.text(
            -1,
            _y_max + _y_tick / 2,
            f"{info['name']}({info.code}) - {info.industry}({on}) - {info.title} - [{info.revenue}]",
            fontsize=40,
            color='white'
        )

        last = self._c_watch.get_last()
        for name, c in self.text.items():
            text.add(name, c, last[c], offset_x=1.5)

    # 繪製K線
    def _plot_k(self):
        d = self._c_watch.get()
        x_data = np.arange(len(d))

        collections = mutils._construct_candlestick_collections(
            x_data,
            d[data.OPEN],
            d[data.HIGH],
            d[data.LOW],
            d[data.CLOSE],
            marketcolors=self._color(), config=dict(_width_config=self._config(self._c_watch.range))
        )

        self._axes.set_ylim(d[data.LOW].min(), d[data.HIGH].max())

        for c in collections:
            self._axes.add_collection(c)

        self._major()

    # 設定檔
    def _config(self, data_len):
        def lw(name):
            return mwidths._dfinterpolate(mwidths._widths, data_len, name)

        return {
            'ohlc_ticksize': lw('ow'),
            'ohlc_linewidth': lw('olw'),
            'candle_width': lw('cw'),
            'candle_linewidth': lw('clw'),
            'line_width': lw('lw'),
        }

    # 顏色
    def _color(self):
        default = {
            'up': '#9A0000',
            'down': '#FFFFFF'
        }

        edge = {
            'up': '#FF0000',
            'down': '#FFFFFF'
        }

        return {
            'candle': default,
            'edge': edge,
            'wick': default,
            'ohlc': default,
            'alpha': 1,
        }

    # 設定資料呈現邏輯與格式
    def _major(self):
        self._axes.xaxis.set_major_locator(DateLocator(self._c_watch.date()))
        self._axes.xaxis.set_major_formatter(DateFormatter())

        (y_max, y_min) = self._c_watch.get_y_max_min()
        price_locator = PriceLocator(y_max, y_min)
        self._axes.yaxis.set_major_locator(price_locator)
        self._axes.yaxis.set_major_formatter(PriceFormatter())

    # 副圖
    def _sup_axes(self):
        return {
            'ma': MA(),
            'max_min': MaxMin(),
        }


# 成交量
class Volume(SubAxes):
    # 紅k
    up_color = '#9A0000'

    # 黑k
    down_color = '#23B100'

    font_size = 25

    def _plot(self, **kwargs):
        if len(self._axes.containers) > 0:
            self._axes.containers[0].remove()

        d = self._c_watch.get()
        volumes = d[data.VOLUME]
        x_data = np.arange(len(volumes))
        miny = 0.3 * np.nanmin(volumes)
        maxy = 1.1 * np.nanmax(volumes)
        colors = mplotting._updown_colors(
            self.up_color,
            self.down_color,
            d[data.OPEN],
            d[data.CLOSE],
            use_prev_close=True
        )

        self._axes.set_ylim(miny, maxy)
        self._axes.bar(
            x_data,
            volumes,
            width=0.85,
            linewidth=mwidths._dfinterpolate(mwidths._widths, self._c_watch.range, 'vlw'),
            color=colors,
            ec=mplotting._adjust_color_brightness(colors, 0.90)
        )

        self._major(volumes)
        self._update_label()

    def _plot_text(self, text, **kwargs):
        text.add('量', data.VOLUME, self._c_watch.get_last()[data.VOLUME], offset_x=1.5)

    def _major(self, data):
        fun = lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (
                x * 1e-3) if x >= 1e3 else '%1.0f' % x

        self._axes.yaxis.set_major_locator(VolumeLocator(data))
        self._axes.yaxis.set_major_formatter(mticks.FuncFormatter(fun))

        for ticks in [self._axes.get_yticklabels(), self._axes.get_xticklabels()]:
            for tick in ticks:
                tick.update({'fontsize': self.font_size, 'rotation': 0})

    def clear(self):
        self._axes.clear()

    def remove(self, **kwargs):
        self._axes.remove()


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
        self.day = []

    def _plot(self, **kwargs):
        day = kwargs.get('ma')

        if day == None:
            return

        self.day = day
        data = self._c_watch.get_ma(day)

        for d in day:
            if d not in self._line:
                self._add(d, data[f'{d}ma'])

        day = {d: '' for d in day}

        for d, v in self._line.items():
            if d not in day:
                v.remove()
                del self._line[d]

    def _plot_text(self, text, **kwargs):
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

    def clear(self):
        for name, line in self._line.items():
            line[0].remove()

        self._line.clear()

    def remove(self, **kwargs):
        name = kwargs.get('name')
        if name in self._line[name]:
            self._line[name].remove()
            del self._line[name]


# 最高價與最低價
class MaxMin(SubAxes):
    font_size = 25

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

    def _plot(self, **kwargs):
        y_tick = self._axes.yaxis.major.locator.tick
        (x_max, y_max) = self._c_watch.get_xy_max()
        (x_min, y_min) = self._c_watch.get_xy_min()

        self._max = self._set(x_max, y_max, y_offset=(y_tick / 2))
        self._min = self._set(x_min, y_min, y_offset=-y_tick)

    def _set(self, x, y, y_offset=0.0):
        return self._axes.annotate(
            y,
            xy=(x, y),
            xytext=(x - self.offset_x[len(str(y))], y + y_offset),
            color='black',
            size=self.font_size,
            arrowprops=dict(arrowstyle="simple"),
            bbox=dict(boxstyle='square', fc="0.5")
        )

    def clear(self):
        self.remove()

    def remove(self, **kwargs):
        if self._max != None:
            self._max.remove()

        if self._min != None:
            self._min.remove()


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

        self._style = dict(color='#FFFF66', linewidth=1)
        self._isPress = False

    def set_data(self, data):
        self._data = data

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
        if event.button == MouseButton.LEFT:
            self._isPress = True
            self.draw(event)
        elif event.button == MouseButton.RIGHT:
            self.clear()
            self.canvas.draw_idle()

    # 釋放
    def on_release(self, event):
        self._isPress = False

    # 移動
    def move(self, event):
        if self._isPress:
            self.draw(event)

    # 清空游標
    def clear(self):
        for ax in self._vax.values():
            ax.set_visible(False)

        for ax in self._hax.values():
            ax.set_visible(False)


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

        start = (self._min - (self._min % self.tick)) - self.tick

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
