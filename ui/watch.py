# -*- coding: utf-8 -*-
import math
import tkinter as tk
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticks
from stock import data
from . import other, k
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

        self.k_watch = data.K(other.stock_csv_path(self.config))
        self.k = None
        self.trend_watch = data.Tick(other.stock_tick_csv_path(self.config))
        self.trend = None

        self._use_style()

    # 繪製
    def plot(self, code, date=None, panel_ratios=None, **kwargs):
        if self._fig is not None:
            self.clear()
        else:
            self._fig = plt.figure()
            self._fig.set_size_inches((self.width / 100, self.height / 100))
            self.canvas = FigureCanvasTkAgg(self._fig, self._frame)

        self.kwargs = kwargs
        type = kwargs.get('type')

        if type == 'k':
            self._plot_k(code, date=date, panel_ratios=panel_ratios, **kwargs)
        elif type == 'trend':
            self._plot_trend(code, date=date, panel_ratios=panel_ratios, **kwargs)

        self.canvas.draw_idle()

        return self._fig

    # 繪製某個股
    def update_plot(self, code, date=None):
        if self.kwargs.get('k'):
            self._plot_k(code, date=date, **self.kwargs)
        elif self.kwargs.get('trend'):
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


# K線看盤
class KWatch():
    def __init__(self, fig, canvas, watch):
        self._fig = fig
        self._c_watch = None
        self.watch = watch
        self.canvas = canvas
        self._data_text = None
        self.event = None
        self._axes = {}

    def plot(self, code, date=None, **kwargs):
        c_watch = self.watch.code(code, date=date)
        if c_watch is None:
            return False

        if len(self._axes) == 0:
            axes_list = _build_axes(self._fig, panel_ratios=kwargs.get('panel_ratios'))
            self._data_test(axes_list[-1])

            i = 0
            for name, object in self._master_axse().items():
                object.draw(code, axes_list[i], self._data_text, c_watch, self.watch, **kwargs)
                self._axes[name] = object
                i += 1

            self.event = k.KMoveEvent(self.canvas, c_watch, [a.axes for a in self._axes.values()])
            self.event.add_callback(self.event_show_data)

        else:
            self._data_text.clear()

            for object in self._axes.values():
                object.re_draw(code, object.axes, self._data_text, c_watch, self.watch, **kwargs)

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


class TrendWatch():
    xy_font_size = 25

    def __init__(self, fig, canvas, watch, stock):
        self._fig = fig
        self.canvas = canvas
        self.watch = watch
        self.stock = stock
        self._axes = {}
        self._data_text = None

    def plot(self, code, date=None, **kwargs):
        c_watch = self.watch.code(code, date)
        if c_watch is None:
            return False

        if date is None:
            date = c_watch.loc['time'][0][:10]

        yesterday = self.stock.yesterday(code, date)
        if yesterday is None:
            return False

        volume = c_watch.loc[data.VOLUME].dropna().astype(int)

        axes_list = _build_axes(self._fig, panel_ratios=(4, 1))
        axes_list[0].xaxis.set_major_locator(TimeLocator())
        axes_list[0].xaxis.set_major_formatter(TimeFormatter())
        axes_list[1].xaxis.set_major_locator(TimeLocator())
        axes_list[1].xaxis.set_major_formatter(TimeFormatter())

        price_loc = PriceLocator(yesterday['close'])
        axes_list[0].yaxis.set_major_locator(price_loc)
        axes_list[0].yaxis.set_major_formatter(PriceFormatter(yesterday['close']))
        axes_list[1].yaxis.set_major_locator(k.VolumeLocator(volume, len=3))

        axes_list[1].set_ylim(0, 1.1 * volume.max())

        fun = lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (
                x * 1e-3) if x >= 1e3 else '%1.0f' % x
        axes_list[1].yaxis.set_major_formatter(mticks.FuncFormatter(fun))

        axes_list[0].set_xlim(-5, 270)
        axes_list[0].set_ylim(price_loc.min, price_loc.max)

        axes_list[0].axhline(y=(yesterday['close']), color='#335867')
        axes_list[0].tick_params(axis='y', labelsize=self.xy_font_size)
        axes_list[0].tick_params(axis='x', labelsize=self.xy_font_size)
        axes_list[1].tick_params(axis='y', labelsize=self.xy_font_size)
        axes_list[1].tick_params(axis='x', labelsize=self.xy_font_size, labelcolor='#FFFF00')

        y_label = axes_list[0].get_yticklabels()
        y_label[0].set_bbox(dict(facecolor='green'))
        y_label[-1].set_bbox(dict(facecolor='red'))
        close_pos = math.ceil(len(y_label) / 2)

        for l in y_label[1:close_pos - 1]:
            l.set_color('#51F069')

        for l in y_label[close_pos:-1]:
            l.set_color('#FF0000')

        date_times = pd.date_range(start='2020-01-01 09:00:00', end=f'2020-01-01 13:33:00', freq='min')
        for i in range(4):
            date_times = date_times.delete(266)

        times = {t.strftime('%H:%M:%S'): i for i, t in enumerate(date_times)}

        x = [i - 5 for i in range(6)]
        y = [yesterday['close'] for i in range(6)]
        yv = [0 for i in range(6)]
        p = c_watch.loc['price'].dropna().astype(float)

        for i, t in enumerate(c_watch.loc['time'].dropna()):
            x.append(times[t[11:]])
            y.append(p[i])
            yv.append(volume[i])

        axes_list[0].plot(x, y, color='#FFFF00')
        axes_list[1].bar(x, yv, color='#FF00FF', width=0.2)

        y_max = p.max()
        x_max = int(p.idxmax())
        axes_list[0].annotate(
            y_max,
            xy=(x_max, y_max + 0.5 * 2),
            xytext=(x_max + 5, y_max + 0.5),
            color='#FF0000',
            size=self.xy_font_size,
            arrowprops=dict(arrowstyle="simple", color='#FF0000'),
        )

        y_min = p.min()
        x_min = int(p.idxmin())
        axes_list[0].annotate(
            y_min,
            xy=(x_min, y_min - 0.5 * 2),
            xytext=(x_min + 5, y_min - 0.5 * 4),
            color='#51F069',
            size=self.xy_font_size,
            arrowprops=dict(arrowstyle="simple", color='#51F069'),
        )

        axes_list[0].grid(True)
        axes_list[1].grid(True)


# 日期塞選
class TimeLocator(mticks.Locator):
    def __call__(self):
        return [0, 60, 120, 180, 240]


# 日期格式
class TimeFormatter(mticks.Formatter):
    date = {
        0: 9,
        60: 10,
        120: 11,
        180: 12,
        240: 13,
    }

    def __call__(self, x, pos=None):
        return self.date[x]


# 股價塞選
class PriceLocator(mticks.Locator):
    def __init__(self, close):
        self.close = close
        self.max = self.get_max(self.close)
        self.min = self.get_min(self.close)
        self.ticks = []

    def __call__(self):
        if len(self.ticks) > 0:
            return self.ticks

        self.ticks = self.tick_values(None, None)
        return self.ticks

    def tick_values(self, vmin, vmax):
        f_len = self.get_len(self.close)
        tick = self.get_tick(self.close)
        list = []

        # 當走勢y軸每個間隔都可以一直時就直接以此間隔做y軸計算
        # 1. 漲停與跌停價不能跨tick
        # 2. 第二低跌停股價與其他y軸價格差異需一致
        # 如昨日收盤31.9 漲停35.05 跌停28.75，此時每一個y軸價格間距為1.05
        t = round((self.close - self.min) / 3, f_len)
        if (self.get_tick(self.min) == self.get_tick(self.max)) & (round(t % tick, f_len) == tick):
            [list.append(round(self.min + (i * t), f_len)) for i in range(6)]
        else:
            # 由於y軸間價格間距無法計算出統一差異，所以定義除了第二低跌停股價差異跟其他價格不同
            # 如昨日收盤17.6 跌停15.85 漲停19.35，第二跌停價為16.25，所以16.25 - 15.85 = 0.4
            # 第三跌停價之後為16.7/17.15/17.6，17.15 - 16.7 = 0.45，之後y軸都是0.45價格差異
            list.append(self.min)

            t = self.get_tick(self.close)
            num = round((self.close - self.min) / t) / 4
            yt = math.ceil(num) * t

            [list.append(round(self.close - (yt * i), f_len)) for i in sorted(range(4), reverse=True)]
            [list.append(round(self.close + (yt * (i + 1)), f_len)) for i in range(3)]

        list.append(self.max)

        return list

    # 股價tick
    def get_tick(self, close):
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
    def get_len(self, close):
        if close < 50:
            return 2
        elif close < 500:
            return 1

        return 0

    # 漲停價
    def get_max(self, close):
        # 漲停價為昨日收盤價上漲10%
        max = round(close * 1.1, self.get_len(close))
        mc = close

        # 由於漲幅會受到股價不同區間而tick不同，
        # 所以在計算股價時如果有跨區間時tick不同會造成計算漲幅超過10%
        # 如昨日收盤價51.2，跌停為46.1，漲停為56.3，但tick跨越0.05跟0.1
        # 到了50元股價就不能用0.05來計算否則會超過10%限制
        while True:
            t = self.get_tick(mc)

            if max <= mc:
                if round((((mc / close) - 1) * 100), 2) > 10:
                    max = mc - t

                max = round(max, self.get_len(max))
                break

            mc = mc + t
            mc = round(mc, self.get_len(mc))

        return max

    # 跌停價
    def get_min(self, close):
        # 跌停價為昨日收盤價下跌10%
        min = round(close * 0.9, self.get_len(close))
        mc = close

        # 由於漲幅會受到股價不同區間而tick不同，
        # 所以在計算股價時如果有跨區間時tick不同會造成計算漲幅超過10%
        # 如昨日收盤價51.2，跌停為46.1，漲停為56.3，但tick跨越0.05跟0.1
        # 到了50元股價就不能用0.05來計算否則會超過10%限制
        while True:
            t = self.get_tick(mc)

            if min >= mc:
                if round(((mc / close) - 1) * -100, 2) > 10:
                    min = mc + t

                min = round(min, self.get_len(min))
                break

            mc = mc - t
            mc = round(mc, self.get_len(mc))

        return min


# 股價格式
class PriceFormatter(mticks.Formatter):
    len = 0

    def __init__(self, close):
        if close < 50:
            self.len = 2
        elif close < 500:
            self.len = 1

    def __call__(self, x, pos=None):
        if self.len == 2:
            return '%1.2f' % x
        elif self.len == 1:
            return '%1.1f' % x

        return int(x)


# 繪製畫板
def _build_axes(fig, panel_ratios=None):
    left_pad = 0.108
    right_pad = 0.055
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

    # axes.append(fig.add_axes([0, bot_pad, 1 - (plot_width + right_pad), hs['height'].sum()]))

    return axes
