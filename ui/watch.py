# -- coding: utf-8 --

import os
import tkinter as tk
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticks
import mplfinance._utils as mutils
import mplfinance._widths as mwidths
import mplfinance.plotting as mplotting
from stock import data
from datetime import datetime
from mplfinance._styledata import charles
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Watch():
    xy_data_style = {'fontsize': 28, 'rotation': 0}

    main_panel = 0

    def __init__(self, master, config=None, **kwargs):
        self._master = master
        self._fig = None
        self._axs = None
        self.canvas = None
        self.event = None

        self._main_axes = None
        self._sub_axes = {}
        self._apply_axes = {}
        self.text = None
        self.info = None

        self.watch = data.Watch(os.path.join(config['data'], 'csv'), **kwargs)

    # 繪製
    def plot(self, code, width=100, height=100, date=None, **kwargs):
        self.data = self.watch.code(code, date=date)
        self.kwargs = kwargs

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

        self._set_main_axes(code, self._axs[self.main_panel])
        self._set_sup_axes({data.VOLUME: self._axs[2]})
        self._update_label()

        return self._fig

    # 繪製某個股
    def plot_code(self, code, date=None):
        c_data = self.watch.code(code, date=date)
        if c_data == None:
            return False

        self.data = c_data
        d = self.data.get()
        x_data = np.arange(len(d))

        config = mwidths._determine_width_config(x_data, dict(
            show_nontrading=False,
            width_adjuster_version=None,
            scale_width_adjustment=None,
            update_width_config=self._update_width_config()
        ))

        collections = mutils._construct_candlestick_collections(
            x_data,
            d[data.OPEN],
            d[data.HIGH],
            d[data.LOW],
            d[data.CLOSE],
            marketcolors=self._get_style()['marketcolors'], config=dict(_width_config=config)
        )

        self._main_axes.set_ylim(d[data.LOW].min(), d[data.HIGH].max())
        if len(self._main_axes.collections) > 0:
            self._main_axes.collections[0].remove()
            self._main_axes.collections[0].remove()

        for c in collections:
            self._main_axes.add_collection(c)

        if self.text != None:
            self.text.clear()

        if self.info != None:
            self.info.remove()

        for ax in self._apply_axes.values():
            ax.clear()
        for ax in self._sub_axes.values():
            ax.clear()

        self._sub_axes.clear()
        self._apply_axes.clear()

        self._set_main_axes(code, self._axs[self.main_panel])
        self._set_sup_axes({data.VOLUME: self._axs[2]})
        self._update_label()

        self.event.clear()
        self.event.set_data(self.data)
        self.canvas.draw_idle()

        return True

    def _k(self):
        pass

    # 設定資料呈現邏輯與格式
    def _major(self):
        self._main_axes.xaxis.set_major_locator(DateLocator(self.data.date()))
        self._main_axes.xaxis.set_major_formatter(DateFormatter())

        (y_max, y_min) = self.data.get_y_max_min()
        price_locator = PriceLocator(y_max, y_min)
        self._main_axes.yaxis.set_major_locator(price_locator)
        self._main_axes.yaxis.set_major_formatter(PriceFormatter())

    # 主圖設定
    def _set_main_axes(self, code, axes):
        y_max, y_min = self.data.get_y_max_min()
        axes.name = data.CLOSE
        axes.set_xlim(-0.5, self.data.range - 0.5)
        axes.set_ylim(y_min, y_max)
        self._main_axes = axes

        self._major()

        plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']
        plt.rcParams['axes.unicode_minus'] = False

        self._y_tick = axes.yaxis.major.locator.tick
        self._y_max = axes.yaxis.major.locator.get_ticks()[-1]

        info = self.watch.info(code)

        if info.on == 1:
            on = '上市'
        else:
            on = '上櫃'

        self.text = DataLabel(self._main_axes, self.data.get().iloc[-1], x_min=-8)
        self.info = axes.text(
            -1,
            self._y_max + self._y_tick / 2,
            f"{info['name']}({info.code}) - {info.industry}({on}) - {info.title} - [{info.revenue}]",
            fontsize=40,
            color='white'
        )

        axes_list = {
            'ma': MA(),
            'max_min': MaxMin(),
        }

        for name, object in axes_list.items():
            self._plot_sup_axes(self._main_axes, object)
            self._apply_axes[name] = object

    # 附圖設定
    def _set_sup_axes(self, axes_list):
        sup = {
            data.VOLUME: Volume(),
        }

        for name, axes in axes_list.items():
            if name in sup:
                axes.name = name
                object = sup[name]
                self._plot_sup_axes(axes, object)
                self._sub_axes[name] = object

    def _plot_sup_axes(self, axes, object):
        object.set_axes(axes)
        object.plot(self._fig, self.data, **self.kwargs)
        object.plot_text(self.text, self.data, **self.kwargs)

    # 更新label
    def _update_label(self):
        for l in self._main_axes.get_yticklabels():
            l.update(self.xy_data_style)

        for l in self._main_axes.get_xticklabels():
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

    text = {
        'd': data.DATE,
        'o': data.OPEN,
        'c': data.CLOSE,
        'h': data.HIGH,
        'l': data.LOW,
        'v': data.VOLUME,
    }

    def __init__(self, axes, data, x_min=0):
        self._axes = axes

        self._title = {}
        self._value = {}

        self._x_min = x_min
        self._y_max = axes.yaxis.major.locator.get_ticks()[-1]
        self._y_tick = axes.yaxis.major.locator.tick

        for n, c in self.text.items():
            self.add(n, c, data[c], offset_x=1.5)

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
    def __init__(self):
        self._line = {}

    def set_axes(self, axes):
        self._axes = axes

    def plot(self, figure, data, **kwargs):
        pass

    def plot_text(self, text, data, **kwargs):
        pass

    def clear(self):
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
        self.ma = None

    def plot(self, figure, data, **kwargs):
        ma = kwargs.get('ma')

        if ma == None:
            return

        self.ma = ma
        self._plot(data, ma)

    def _plot(self, data, day):
        data = data.get_ma(day)

        for d in day:
            if d not in self._line:
                self._add(d, data[f'{d}ma'])

        day = {d: '' for d in day}

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

    def plot(self, figure, data, **kwargs):
        self._plot(data)

    def _plot(self, data):
        y_tick = self._axes.yaxis.major.locator.tick
        (x_max, y_max) = data.get_xy_max()
        (x_min, y_min) = data.get_xy_min()

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


# 成交量
class Volume(SubAxes):
    # 紅k
    up_color = '#9A0000'

    # 黑k
    down_color = '#23B100'

    font_size = 25

    def plot(self, figure, data, **kwargs):
        self._plot(data)

    def _plot(self, data):
        if len(self._axes.containers) > 0:
            self._axes.containers[0].remove()

        volumes = data.volume()
        x_data = np.arange(len(volumes))
        miny = 0.3 * np.nanmin(volumes)
        maxy = 1.1 * np.nanmax(volumes)
        colors = self._colors(data.open(), data.close())
        config = mwidths._determine_width_config(x_data, dict(
            show_nontrading=False,
            width_adjuster_version=None,
            scale_width_adjustment=None,
            update_width_config={'volume_width': 0.85}
        ))

        self._axes.set_ylim(miny, maxy)
        self._axes.bar(
            x_data,
            volumes,
            width=config['volume_width'],
            linewidth=config['volume_linewidth'],
            color=colors,
            ec=mplotting._adjust_color_brightness(colors, 0.90)
        )

        self._major(volumes)

    def _major(self, data):
        fun = lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (
                x * 1e-3) if x >= 1e3 else '%1.0f' % x

        self._axes.yaxis.set_major_locator(VolumeLocator(data))
        self._axes.yaxis.set_major_formatter(mticks.FuncFormatter(fun))

        for ticks in [self._axes.get_yticklabels(), self._axes.get_xticklabels()]:
            for tick in ticks:
                tick.update({'fontsize': self.font_size, 'rotation': 0})

    def update(self, data):
        self._plot(data)

    def _colors(self, open, close):
        return mplotting._updown_colors(self.up_color, self.down_color, open, close, use_prev_close=True)

    def clear(self):
        self._axes.clear()

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
