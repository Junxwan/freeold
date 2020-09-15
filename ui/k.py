import tkinter as tk
import numpy as np
import matplotlib.ticker as mticks
import mplfinance._utils as mutils
import mplfinance._widths as mwidths
import mplfinance.plotting as mplotting
from stock import data
from datetime import datetime
from matplotlib.backend_bases import MouseButton


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
            if name == data.DATE:
                p = value[name]
            else:
                p = '%1.2f' % value[name]

            ax.set_text(p)


class SubAxes():
    xy_font_size = 15

    def __init__(self):
        self._sup = {}
        self._line = {}
        self.code = None
        self._watch = None
        self._c_watch = None
        self.axes = None

    def draw(self, code, axes, text, c_watch, watch, **kwargs) -> bool:
        self.code = code
        self.axes = axes
        self._c_watch = c_watch
        self._watch = watch

        if self._plot(**kwargs) == False:
            return False

        self._plot_text(text, **kwargs)

        if self._load_sup(text, **kwargs) == False:
            return False

        return True

    def re_draw(self, code, axes, text, c_watch, watch, **kwargs) -> bool:
        self.clear()
        return self.draw(code, axes, text, c_watch, watch, **kwargs)

    def _plot(self, **kwargs) -> bool:
        return True

    def _plot_text(self, text, **kwargs):
        pass

    def _load_sup(self, text, **kwargs) -> bool:
        for name, o in self._sup_axes().items():
            if isinstance(o, SubAxes) == False:
                return False

            if o.draw(self.code, self.axes, text, self._c_watch, self._watch, **kwargs) == False:
                return False
            self._sup[name] = o

        return True

    def _sup_axes(self):
        return {}

    # 更新label
    def _update_label(self):
        self.axes.tick_params(axis='y', labelsize=self.xy_font_size)
        self.axes.tick_params(axis='x', labelsize=self.xy_font_size)

    def clear_sup(self):
        for a in self._sup.values():
            if isinstance(a, SubAxes):
                a._clear()

    def clear(self):
        self.clear_sup()
        self._clear()

    def _clear(self):
        pass

    def remove(self):
        self._remove()

        for n, o in self._sup.items():
            o.remove()
        for n, o in self._line.items():
            o[0].remove()

        self._line.clear()
        self._sup.clear()

    def _remove(self):
        pass


# K線
class Watch(SubAxes):
    text = {
        '日': data.DATE,
        '開': data.OPEN,
        '收': data.CLOSE,
        '高': data.HIGH,
        '低': data.LOW,
        '漲': data.INCREASE,
        '量': data.VOLUME,
        '振': data.AMPLITUDE,
    }

    def __init__(self):
        SubAxes.__init__(self)
        self.info = None

    # 繪製主圖
    def _plot(self, **kwargs):
        self.axes.name = data.CLOSE
        y_max, y_min = self._c_watch.get_y_max_min()
        self.axes.set_xlim(-2, self._c_watch.range)
        self.axes.set_ylim(y_min, y_max)
        self.axes.yaxis.tick_right()
        self.axes.tick_params(axis='x', rotation=90)
        self.axes.grid(True)

        self._plot_k()
        self._update_label()

        return True

    # 繪製文案
    def _plot_text(self, text, **kwargs):
        info = self._watch.info(self.code)

        if info.on == 1:
            on = '上市'
        else:
            on = '上櫃'

        _y_tick = self.axes.yaxis.major.locator.tick
        _y_max = self.axes.yaxis.major.locator.get_ticks()[-1]

        self.info = self.axes.text(
            -1,
            _y_max + _y_tick / 2,
            f"{info['name']}({info.code}) - {info.industry}({on}) - {info.title} - [{info.revenue}]",
            fontsize=40,
            color='white'
        )

        last = self._c_watch.get_last()
        for name, c in self.text.items():
            text.add(name, c, last[c], offset_x=0.7)

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

        self.axes.set_ylim(d[data.LOW].min(), d[data.HIGH].max())

        for c in collections:
            self.axes.add_collection(c)

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
        self.axes.xaxis.set_major_locator(DateLocator(self._c_watch.date()))
        self.axes.xaxis.set_major_formatter(DateFormatter())

        (y_max, y_min) = self._c_watch.get_y_max_min()
        price_locator = PriceLocator(y_max, y_min)
        self.axes.yaxis.set_major_locator(price_locator)
        self.axes.yaxis.set_major_formatter(PriceFormatter())

    # 副圖
    def _sup_axes(self):
        return {
            'ma': MA(),
            'max_min': MaxMin(),
        }

    def _clear(self):
        self.info.set_text('')
        if len(self.axes.collections) > 0:
            self.axes.collections[0].remove()
            self.axes.collections[0].remove()

    def _remove(self):
        self.info.remove()


# 成交量
class Volume(SubAxes):
    # 紅k
    up_color = '#9A0000'

    # 黑k
    down_color = '#23B100'

    font_size = 25

    def _plot(self, **kwargs):
        self.axes.name = data.VOLUME
        self.axes.grid(True)
        self.axes.yaxis.tick_right()

        if len(self.axes.containers) > 0:
            self.axes.containers[0].remove()

        d = self._c_watch.get()
        volumes = d[data.VOLUME]
        x_data = np.arange(len(volumes))
        colors = mplotting._updown_colors(
            self.up_color,
            self.down_color,
            d[data.OPEN],
            d[data.CLOSE],
            use_prev_close=True
        )

        self.axes.set_ylim(0.3 * np.nanmin(volumes), 1.1 * np.nanmax(volumes))
        self.axes.bar(
            x_data,
            volumes,
            width=0.85,
            linewidth=mwidths._dfinterpolate(mwidths._widths, self._c_watch.range, 'vlw'),
            color=colors,
            ec=mplotting._adjust_color_brightness(colors, 0.90)
        )

        self._major(volumes)
        self._update_label()

    def _major(self, volume):
        fun = lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (
                x * 1e-3) if x >= 1e3 else '%1.0f' % x

        self.axes.yaxis.set_major_locator(VolumeLocator(volume))
        self.axes.yaxis.set_major_formatter(mticks.FuncFormatter(fun))

        for ticks in [self.axes.get_yticklabels(), self.axes.get_xticklabels()]:
            for tick in ticks:
                tick.update({'fontsize': self.font_size, 'rotation': 0})

    def _clear(self):
        if len(self.axes.containers) > 0:
            self.axes.containers[0].remove()


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

        if day is None:
            return

        self.day = day
        ma = self._c_watch.get_ma(day)

        for d in day:
            if d not in self._line:
                self._add(d, ma[f'{d}ma'])

        day = {d: '' for d in day}

        for d, v in self._line.items():
            if d not in day:
                v.remove()
                del self._line[d]

    def _plot_text(self, text, **kwargs):
        for name, line in self._line.items():
            key = f'{name}ma'
            text.add(key, key, self._line[name][0].get_ydata()[-1], color=self.color[name], offset_x=1.2)

    def _add(self, day, price):
        if day in self.color:
            color = self.color[day]
        else:
            color = 'red'

        line = self.axes.plot(
            np.arange(len(price)),
            price,
            linewidth=self.line_width,
            color=color,
        )

        self._line[day] = line

        return line

    def _clear(self):
        for name, line in self._line.items():
            line[0].remove()

        self._line.clear()


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
        y_tick = self.axes.yaxis.major.locator.tick
        (x_max, y_max) = self._c_watch.get_xy_max()
        (x_min, y_min) = self._c_watch.get_xy_min()

        self._max = self._set(x_max, y_max, y_offset=(y_tick / 2))
        self._min = self._set(x_min, y_min, y_offset=-y_tick)

    def _set(self, x, y, y_offset=0.0):
        return self.axes.annotate(
            y,
            xy=(x, y),
            xytext=(x - self.offset_x[len(str(y))], y + y_offset),
            color='black',
            size=self.font_size,
            arrowprops=dict(arrowstyle="simple"),
            bbox=dict(boxstyle='square', fc="0.5")
        )

    def _clear(self):
        if self._max is not None:
            self._max.remove()

        if self._min is not None:
            self._min.remove()


# K線事件
class KMoveEvent(tk.Frame):
    def __init__(self, canvas, c_watch, axs):
        tk.Frame.__init__(self)

        self._data = c_watch
        self.canvas = canvas
        self._axs = axs
        self._date = None

        self._vax = {}
        self._hax = {}
        self._callbacks = []

        self.moveEvent = self.canvas.mpl_connect('motion_notify_event', self.move)
        self.clickEvent = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.releaseEvent = self.canvas.mpl_connect('button_release_event', self.on_release)

        self._style = dict(color='#FFFF66', linewidth=1)
        self._isPress = False

    def set_data(self, c_watch):
        self._data = c_watch

    # 事件
    def add_callback(self, fun):
        self._callbacks.append(fun)

    # 重畫
    def draw(self, event):
        if event.xdata is None:
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

        if self._date == None:
            self._date = self._axs[-1].text(int(x - 3), -5, p[data.DATE], fontsize='30', color='#00FFFF')
        else:
            self._date.set_visible(True)
            self._date.set_text(p[data.DATE])
            self._date.set_position((int(x - 3), -5))

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

    def remove(self):
        for ax in self._vax.values():
            ax.remove()

        for ax in self._hax.values():
            ax.remove()

        self._date.remove()
        self.canvas.mpl_disconnect(self.moveEvent)
        self.canvas.mpl_disconnect(self.clickEvent)
        self.canvas.mpl_disconnect(self.releaseEvent)

    # 清空游標
    def clear(self):
        if self._date is not None:
            self._date.set_text('')

        for ax in self._vax.values():
            ax.set_visible(False)

        for ax in self._hax.values():
            ax.set_visible(False)


# 日期塞選
class DateLocator(mticks.Locator):
    def __init__(self, date):
        self.data = date
        self.loc = []

    def __call__(self):
        if len(self.loc) > 0:
            return self.loc
        return self.tick_values(None, None)

    def tick_values(self, vmin, vmax):
        monthFirstWorkDay = {}

        for i, d in enumerate(self.data):
            d = datetime.fromisoformat(d)
            if d.month not in monthFirstWorkDay:
                monthFirstWorkDay[d.month] = i

        self.loc = list(monthFirstWorkDay.values())
        self.loc.append(len(self.data) - 1)

        return self.loc


# 股價塞選
class PriceLocator(mticks.Locator):
    _tick_level = [50, 25, 10, 7.5, 5, 2.5, 1, 0.5, 0.25, 0.1, 0.05]

    def __init__(self, mx, mi):
        self._mx = mx
        self._mi = mi
        self.ticks = []

        diff = mx - mi
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

        start = (self._mi - (self._mi % self.tick)) - self.tick

        for i in range(25):
            p = start + (self.tick * i)
            self.ticks.append(start + (self.tick * i))

            if p > self._mx:
                self.ticks.insert(0, start - self.tick)
                self.ticks.append(p + self.tick)
                break

        self.axis.set_view_interval(self.ticks[0], self.ticks[-1])

        return np.asarray(self.ticks)


# 交易量塞選
class VolumeLocator(mticks.Locator):
    def __init__(self, c_watch, len=5):
        self._c_watch = c_watch
        self.len = len
        self.locs = []

    def __call__(self):
        return self.tick_values(None, None)

    def tick_values(self, vmin, vmax):
        if len(self.locs) > 0:
            return self.locs

        mx = self._c_watch.max()
        mi = self._c_watch.min()
        step = 10 ** (len(str(int((mx - mi) / 3))) - 1)
        diff = (mx - mi) / 3
        step = int((diff - diff % step) + step)

        self.locs = [step * i for i in range(self.len)]

        return self.locs


# 日期格式
class DateFormatter(mticks.Formatter):
    def __call__(self, x, pos=0):
        if x < 0:
            return ''
        return self.axis.major.locator.data[x]

    def get_ticks(self):
        if len(self.locs) == 0:
            self.locs = self.axis.major.locator.loc

        return [self.__call__(x, 0) for x in self.locs]


# 股價格式
class PriceFormatter(mticks.Formatter):
    def __call__(self, x, pos=None):
        if pos == 0:
            return ''

        return '%1.2f' % x
