# -*- coding: utf-8 -*-
import tkinter as tk
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from stock import data
from . import other, k, trend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Watch():
    xy_data_style = {'fontsize': 28, 'rotation': 0}

    main_panel = 0

    def __init__(self, frame, config=None, width=100, height=100, ready=None):
        self._frame = frame
        self._fig = None
        self.config = config
        self.canvas = None
        self.width = width
        self.height = height
        self.ready = ready
        self.type = ''

        self.k_watch = data.K(other.stock_csv_path(self.config))
        self.k = None
        self.trend_watch = data.Trend(other.stock_trend_csv_path(self.config))
        self.trend = None
        self.k_trend = None

        self._use_style()

    # 繪製
    def plot(self, code, date=None, **kwargs):
        if self._fig is not None:
            self.clear()
        else:
            self._fig = plt.figure()
            self._fig.set_size_inches((self.width / 100, self.height / 100))
            self.canvas = FigureCanvasTkAgg(self._fig, self._frame)

        self.kwargs = kwargs
        self.update_plot(code, date=date)

        return self._fig

    # 繪製某個股
    def update_plot(self, code, date=None):
        type = self.kwargs.get('type')

        if type == 'k':
            self._plot_k(code, date=date, **self.kwargs)
        elif type == 'trend':
            self._plot_trend(code, date=date, **self.kwargs)
        elif type == 'k_trend':
            self._plot_k_trend(code, date=date, **self.kwargs)

        self.canvas.draw_idle()

        return True

    # K線看盤
    def _plot_k(self, code, date=None, **kwargs):
        if self.k is None:
            self.k = KWatch(
                self._fig,
                self.canvas,
                self.k_watch,
            )

        self.k.plot(code, date=date, **kwargs)

    # 走勢圖看盤
    def _plot_trend(self, code, date=None, **kwargs):
        if self.trend is None:
            self.trend = TrendWatch(
                self._fig,
                self.canvas,
                self.trend_watch,
                self.k_watch.get_stock(),
            )

        self.trend.plot(code, date=date, **kwargs)

    def _plot_k_trend(self, code, date=None, **kwargs):
        if self.k_trend is None:
            self.k_trend = KTrendWatch(
                self._fig,
                self.canvas,
                self.k_watch,
                self.trend_watch,
                self.k_watch.get_stock(),
            )

        self.k_trend.plot(code, date=date, **kwargs)

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

    def clear(self):
        for ax in [self.k, self.trend]:
            if ax is not None:
                ax.remove()

        self._fig.clear()

    # 執行
    def pack(self):
        self.canvas.draw()
        self.canvas.get_tk_widget().focus_force()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


class Plot():
    name = ''

    def __init__(self, fig, canvas):
        self._fig = fig
        self.canvas = canvas
        self._data_text = None
        self.event = None
        self._axes = {}

    def plot(self, code, date=None, **kwargs):
        c_watch = self._get(code, date)
        if c_watch is None:
            return False

        if len(self._axes) == 0:
            self._create_axes(code, c_watch, **kwargs)
        else:
            self._update_axes(code, c_watch, **kwargs)

    def _create_axes(self, code, c_watch, **kwargs):
        axes_list = self._build_axes(self._fig, **kwargs)
        self._build_text(axes_list)

        i = 0
        for name, object in self._master_axes().items():
            if self._is_draw(name, **kwargs):
                continue

            if self._draw(code, object, axes_list[i], c_watch, **kwargs) == False:
                return False

            self._axes[name] = object
            i += 1

        self.event = self._build_move_event(c_watch)

        if self.event is not None:
            self.event.add_callback(self.event_show_data)

    def _update_axes(self, code, c_watch, **kwargs):
        self._clear_text()

        for object in self._axes.values():
            object.clear()

            if self._draw(code, object, object.axes, c_watch, **kwargs) == False:
                return False

        if self.event is not None:
            self.event.clear()
            self.event.set_data(self._get_data(c_watch))

    def _draw(self, code, object, axes, c_watch, **kwargs):
        return object.draw(code, axes, self._data_text, c_watch, self._get_watch(), **kwargs)

    def _build_axes(self, fig, **kwargs) -> list:
        return []

    def _build_text(self, axes_list):
        axes = axes_list[-1]
        self._data_text = DataLabel(axes)
        axes.grid(False)
        axes.set_xlim((0, self._data_text.x_max))
        axes.set_ylim((0, self._data_text.y_max))
        axes.set_xticks(np.arange(self._data_text.x_max))
        axes.set_yticks(np.arange(self._data_text.y_max))
        axes.set_xticklabels(['' for i in range(self._data_text.x_max)])

    def _build_move_event(self, c_watch) -> k.MoveEvent:
        return k.MoveEvent(self.canvas, c_watch, [a.axes for a in self._axes.values()])

    def _is_draw(self, name, **kwargs):
        return (name != self.name) & (kwargs.get(name) is None)

    # 主圖清單
    def _master_axes(self) -> dict:
        return {}

    def _get_watch(self):
        return None

    def _get_data(self, c_watch):
        return c_watch

    def event_show_data(self, event, data):
        self._data_text.update(data)

    def _get(self, code, date):
        return None

    def _clear_text(self):
        self._data_text.clear()

    def remove(self):
        self._data_text.remove()
        for n, o in self._axes.items():
            o.remove()
            o.axes.remove()

        self.event.remove()
        self._axes.clear()


# K線看盤
class KWatch(Plot):
    def __init__(self, fig, canvas, watch):
        Plot.__init__(self, fig, canvas)
        self.watch = watch
        self.name = 'k'
        self._c_watch = None

    def _build_axes(self, fig, **kwargs) -> list:
        return _build_axes(fig, panel_ratios=kwargs.get('panel_ratios'))

    def _get(self, code, date=None):
        return self.watch.code(code, date=date)

    def _get_watch(self):
        return self.watch

    # 主圖清單
    def _master_axes(self):
        return {
            'k': k.Watch(),
            data.VOLUME: k.Volume(),
        }


# 日內趨勢看盤
class TrendWatch(Plot):
    def __init__(self, fig, canvas, watch, stock):
        Plot.__init__(self, fig, canvas)
        self.watch = watch
        self.name = 'trend'
        self.stock = stock

    def _build_axes(self, fig, **kwargs) -> list:
        axes = _build_axes(self._fig, panel_ratios=kwargs.get('panel_ratios'), scale_left=0.4, left=False)
        axes[-1].yaxis.tick_right()
        return axes

    def _build_move_event(self, c_watch):
        return trend.MoveEvent(
            self.canvas,
            c_watch.value(),
            [a.axes for a in self._axes.values()],
            show_date=False,
            color='#00FFFF'
        )

    def _get(self, code, date=None):
        return self.watch.get(code, date)

    def _get_watch(self):
        return self.stock

    def _get_data(self, c_watch):
        return c_watch.value()

    # 主圖清單
    def _master_axes(self):
        return {
            'trend': trend.Watch(),
            data.VOLUME: trend.Volume(),
        }

    def _clear(self):
        pass


# K線跟日內趨勢看盤
class KTrendWatch(Plot):
    def __init__(self, fig, canvas, k_watch, trend_watch, stock):
        Plot.__init__(self, fig, canvas)
        self.name = ['k', 'trend']
        self._k_watch = k_watch
        self._trend_watch = trend_watch
        self._stock = stock

    def _is_draw(self, name, **kwargs):
        if name in self.name:
            return False

        return kwargs.get(name.split('_')[1]) is None

    def _draw(self, code, object, axes, c_watch, **kwargs) -> bool:
        if object.master_name == '':
            name = object.name
        else:
            name = object.master_name

        if name == '':
            return False

        if name == k.NAME:
            watch = self._k_watch
        elif name == trend.NAME:
            watch = self._stock
        else:
            return False

        return object.draw(code, axes, self._data_text, c_watch[name], watch, **kwargs)

    def _build_axes(self, fig, **kwargs) -> list:
        return _build_multi_axes(fig, panel_ratios=kwargs.get('panel_ratios'), cols=2)

    def _build_text(self, axes_list):
        pass

    def _get(self, code, date):
        trend = self._trend_watch.get(code, date)
        if trend is None:
            return None

        k = self._k_watch.code(code, date=trend.date)
        if k is None:
            return None

        return {
            'k': k,
            'trend': trend
        }

    def _clear_text(self):
        pass

    # 主圖清單
    def _master_axes(self):
        return {
            'trend': trend.Watch(),
            f'trend_{data.VOLUME}': trend.Volume(),
            'k': k.Watch(),
            f'k_{data.VOLUME}': k.Volume(),
        }


# 即時數據
class DataLabel():
    title_font_size = 28
    value_font_size = 28

    x_max = 3
    y_max = 20

    def __init__(self, axes):
        self._axes = axes
        self._title = {}
        self._value = {}

    def add(self, name, key, value, color='white', offset_x=1.0):
        self.set_title(name, key, color=color)
        self.set_value(key, value, offset_x=offset_x)

    def set_title(self, name, key, color='white'):
        self._title[key] = self._axes.text(
            0.1,
            (self.y_max - 0.5) - len(self._title) - 0.2,
            name,
            fontsize=self.title_font_size,
            color=color
        )

    def set_value(self, name, value, color='black', offset_x=0.0):
        if name not in self._title:
            return

        title = self._title[name]

        self._value[name] = self._axes.text(
            0.1 + offset_x,
            title._y,
            value,
            fontsize=self.value_font_size,
            color=color,
            bbox=dict(boxstyle='square')
        )

    def remove(self, name=None):
        if name is not None:
            if name in self._title:
                self._title[name].remove()
                self._value[name].remove()

                del self._title[name]
                del self._value[name]
        else:
            if self._axes is not None:
                if self._axes.axes is not None:
                    self._axes.remove()
            self.clear()

    def clear(self):
        for v in self._title.values():
            v.remove()
        for v in self._value.values():
            v.remove()

        self._title.clear()
        self._value.clear()

    def update(self, value):
        for name, ax in self._value.items():
            if name not in value:
                continue

            if (name == 'time') | (name == data.DATE):
                p = value[name]
            else:
                p = float(value[name])
                if p < 50:
                    p = '%1.2f' % p
                elif p < 500:
                    p = '%1.1f' % p

            ax.set_text(p)


# 繪製畫板
def _build_axes(fig, panel_ratios=None, scale_left=0.0, left=True):
    left_pad = 0.108
    right_pad = 0.055
    top_pad = 0.12
    bot_pad = 0.036
    plot_height = 1.0 - (bot_pad + top_pad)
    plot_width = 1.0 - (left_pad + right_pad)

    if scale_left > 0:
        left_pad *= scale_left
        right_pad *= (scale_left * 5)

    hs = pd.DataFrame({'height': []})
    if panel_ratios is None:
        hs.at[0, 'height'] = plot_height
    else:
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

    if left:
        axes.append(fig.add_axes([0, bot_pad, 1 - (plot_width + right_pad), hs['height'].sum()]))
    else:
        axes.append(fig.add_axes([plot_width + left_pad, bot_pad, 1 - plot_width, hs['height'].sum()]))

    return axes


# 繪製多層畫板
def _build_multi_axes(fig, panel_ratios=None, rows=1, cols=1, scale_left=1.0, scale_right=1.0):
    left_pad = (0.108 * scale_left) / cols
    right_pad = 0.055 * scale_right
    top_pad = 0.12
    bot_pad = 0.036
    plot_height = (1.0 - (bot_pad + top_pad)) / rows
    plot_width = (1.0 - (left_pad + right_pad)) / cols

    if panel_ratios is None:
        p_len = 1
    else:
        p_len = len(panel_ratios)

    style = []
    for r in range(rows):
        if r == 0:
            tmp_bot_pad = bot_pad
        else:
            tmp_bot_pad = (bot_pad + plot_height) * 1.1

        for c in range(cols):
            if c == 0:
                tmp_left_pad = left_pad
            else:
                tmp_left_pad = left_pad + plot_width

            if panel_ratios is None:
                style.append([tmp_left_pad, tmp_bot_pad, plot_width, plot_height])
            else:
                psum = sum(panel_ratios)

                for panid, size in enumerate(panel_ratios):
                    ratios_bot_pad = tmp_bot_pad
                    if panid + 1 < len(panel_ratios):
                        ratios_bot_pad = tmp_bot_pad + plot_height * panel_ratios[panid + 1] / psum

                    style.append([tmp_left_pad, ratios_bot_pad, plot_width, plot_height * size / psum])

    axes = []
    for index, rows in enumerate(style):
        if (index % p_len) == 0:
            ax = fig.add_axes(rows)
        else:
            ax = fig.add_axes(rows, sharex=axes[index - (p_len - 1)])

        ax.set_axisbelow(True)
        axes.append(ax)

    return axes
