# -*- coding: utf-8 -*-
import math
import tkinter as tk
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticks
from stock import data
from . import other, k, trend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import MouseButton


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

        self.k_watch = data.K(other.stock_csv_path(self.config))
        self.k = None
        self.trend_watch = data.Trend(other.stock_trend_csv_path(self.config))
        self.trend = None

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
        if self.k is not None:
            self.k.remove()

        self._fig.clear()

    # 執行
    def pack(self):
        self.canvas.draw()
        self.canvas.get_tk_widget().focus_force()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


class Plot():
    def __init__(self, fig, canvas, watch):
        self._fig = fig
        self.watch = watch
        self.canvas = canvas
        self._data_text = None
        self.event = None
        self._axes = {}

    def plot(self, code, date=None, **kwargs):
        c_watch = self.watch._get(code, date=date)
        if c_watch is None:
            return False

        if len(self._axes) == 0:
            axes_list = _build_axes(self._fig, panel_ratios=kwargs.get('panel_ratios'))
            self._build_text(axes_list[-1])
        else:
            pass

    def _build_text(self, axes):
        axes.grid(False)
        axes.set_xlim((0, self._data_text.x_max))
        axes.set_ylim((0, self._data_text.y_max))
        axes.set_xticks(np.arange(self._data_text.x_max))
        axes.set_yticks(np.arange(self._data_text.y_max))
        axes.set_xticklabels(['' for i in range(self._data_text.x_max)])

    def _get(self, code, date=None):
        return None


# K線看盤
class KWatch():
    def __init__(self, fig, canvas, watch):
        self._fig = fig
        self.watch = watch
        self.canvas = canvas
        self._data_text = None
        self.event = None
        self._axes = {}

        self._c_watch = None

    def plot(self, code, date=None, **kwargs):
        c_watch = self.watch.code(code, date=date)
        if c_watch is None:
            return False

        if len(self._axes) == 0:
            axes_list = _build_axes(self._fig, panel_ratios=kwargs.get('panel_ratios'))
            self._data_test(axes_list[-1])

            i = 0
            for name, object in self._master_axse().items():
                if object.draw(code, axes_list[i], self._data_text, c_watch, self.watch, **kwargs) == False:
                    return False
                self._axes[name] = object
                i += 1

            self.event = k.KMoveEvent(self.canvas, c_watch, [a.axes for a in self._axes.values()])
            self.event.add_callback(self.event_show_data)

        else:
            self._data_text.clear()

            for object in self._axes.values():
                if object.re_draw(code, object.axes, self._data_text, c_watch, self.watch, **kwargs) == False:
                    return False

            if self.event is not None:
                self.event.clear()
                self.event.set_data(c_watch)

    def _data_test(self, axes):
        self._data_text = k.DataLabel(axes)
        axes.grid(False)
        axes.set_xlim((0, self._data_text.x_max))
        axes.set_ylim((0, self._data_text.y_max))
        axes.set_xticks(np.arange(self._data_text.x_max))
        axes.set_yticks(np.arange(self._data_text.y_max))
        axes.set_xticklabels(['' for i in range(self._data_text.x_max)])

    # 主圖清單
    def _master_axse(self):
        return {
            'k': k.Watch(),
            data.VOLUME: k.Volume(),
        }

    # 即時顯示資料
    def event_show_data(self, event, d):
        self._data_text.update(d)

    def remove(self):
        self._data_text.remove()
        for n, o in self._axes.items():
            o.remove()
            o.axes.remove()

        self.event.remove()
        self._axes.clear()


# 日內趨勢看盤
class TrendWatch():
    def __init__(self, fig, canvas, watch, stock):
        self._fig = fig
        self.watch = watch
        self.canvas = canvas
        self._data_text = None
        self.event = None
        self._axes = {}

        self.stock = stock

    def plot(self, code, date=None, **kwargs):
        c_watch = self.watch.get(code, date)
        if c_watch is None:
            return False

        if len(self._axes) == 0:
            axes_list = _build_axes(self._fig, panel_ratios=(4, 1), scale_left=0.4, left=False)
            self._data_test(axes_list[-1])

            i = 0
            for name, object in self._master_axse().items():
                if object.draw(code, axes_list[i], self._data_text, c_watch, self.stock, **kwargs) == False:
                    return False
                self._axes[name] = object
                i += 1

            self.event = trend.KMoveEvent(self.canvas, c_watch.all(), [a.axes for a in self._axes.values()])
            self.event.add_callback(self.event_show_data)
        else:
            self._data_text.clear()

            for object in self._axes.values():
                if object.re_draw(code, object.axes, self._data_text, c_watch, self.stock, **kwargs) == False:
                    return False

            if self.event is not None:
                self.event.clear()
                self.event.set_data(c_watch.all())

    def _data_test(self, axes):
        axes.yaxis.tick_right()
        self._data_text = trend.DataLabel(axes)
        axes.grid(False)
        axes.set_xlim((0, self._data_text.x_max))
        axes.set_ylim((0, self._data_text.y_max))
        axes.set_xticks(np.arange(self._data_text.x_max))
        axes.set_yticks(np.arange(self._data_text.y_max))
        axes.set_xticklabels(['' for i in range(self._data_text.x_max)])

    # 即時顯示資料
    def event_show_data(self, event, d):
        self._data_text.update(d)

    # 主圖清單
    def _master_axse(self):
        return {
            'trend': trend.Watch(),
            data.VOLUME: trend.Volume(),
        }


# 繪製畫板
def _build_axes(fig, panel_ratios=None, scale_left=1.0, left=True):
    left_pad = 0.108 * scale_left
    right_pad = 0.055 * (scale_left * 5)
    top_pad = 0.12
    bot_pad = 0.036
    plot_height = 1.0 - (bot_pad + top_pad)
    plot_width = 1.0 - (left_pad + right_pad)

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
