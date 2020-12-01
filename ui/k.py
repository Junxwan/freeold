import numpy as np
import matplotlib.ticker as mticks
import mplfinance._utils as mutils
import mplfinance._widths as mwidths
import mplfinance.plotting as mplotting
import matplotlib.pyplot as plt
from stock import data, name
from datetime import datetime

NAME = 'k'


class SubAxes():
    xy_font_size = 28

    name = ''

    master_name = ''

    def __init__(self, font_size=28):
        self._sup = {}
        self.line = {}
        self.code = None
        self._watch = None
        self._c_watch = None
        self.axes = None
        self.ani = None
        self.x = []
        self.y = []
        self._x_data = []
        self._y_data = []
        self.xy_font_size = font_size

    def draw(self, code, axes, text, c_watch, watch, **kwargs) -> bool:
        self.code = code
        self.axes = axes
        self._c_watch = c_watch
        self._watch = watch
        self.info = None

        if self.plot(**kwargs) == False:
            return False

        if text is not None:
            self.plot_text(text, **kwargs)

        self.plot_info()

        if self._load_sup(text, **kwargs) == False:
            return False

        return True

    def plot(self, **kwargs) -> bool:
        return True

    def plot_text(self, text, **kwargs):
        pass

    def plot_info(self):
        pass

    def get_master_name(self):
        if self.master_name == '':
            return self.name

        return self.master_name

    def _load_sup(self, text, **kwargs) -> bool:
        for name, o in self._sup_axes().items():
            if isinstance(o, SubAxes) == False:
                return False

            name_v = kwargs.get(name)

            if (name_v is None) | (name_v is False):
                continue

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

    def stock_info(self):
        info = self._watch.info(self.code)

        if info.on == 1:
            on = '上市'
        else:
            on = '上櫃'

        return f"{info['name']}({info.code}) - {info.industry}({on}) - {info.title} - [{info.revenue}]"

    def clear_sup(self):
        for a in self._sup.values():
            if isinstance(a, SubAxes):
                a._clear()

    def clear(self):
        self.clear_sup()
        self._clear()

        if self.info is not None:
            self.info.remove()

    def _clear(self):
        pass

    def remove(self):
        self._remove()

        for n, o in self._sup.items():
            o.remove()
        for n, o in self.line.items():
            o[0].remove()

        if self.info is not None:
            self.info.remove()
            self.info = None

        self.line.clear()
        self._sup.clear()

    def _remove(self):
        pass


# 事件
class MoveEvent():
    def __init__(self, c_watch, axs, show_date=True, color='#00FFFF', linewidth=2):
        self.set_data(c_watch)
        self._axs = axs
        self.is_show_date = show_date
        self._date = None

        self._vax = {}
        self._hax = {}
        self._callbacks = []

        self._style = dict(color=color, linewidth=linewidth)

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
        y = event.ydata
        p = self.get(x)

        if p is None:
            return

        if len(self._vax) == 0:
            for ax in self._axs:
                self._vax[ax.name] = ax.axvline(x=x, **self._style)
        else:
            for ax in self._vax.values():
                ax.set_visible(True)
                ax.set_xdata(x)

        if self.is_show_date:
            if self._date == None:
                self._date = self._axs[-1].text(int(x - 3), -5, p[data.DATE], fontsize='30', color='#00FFFF')
            else:
                self._date.set_visible(True)
                self._date.set_text(p[data.DATE])
                self._date.set_position((int(x - 3), -5))

        if event.inaxes.name not in self._hax:
            self._hax[event.inaxes.name] = event.inaxes.axhline(y=(y), **self._style)

        for name, ax in self._hax.items():
            if name == event.inaxes.name:
                ax.set_visible(True)
                ax.set_ydata(y)
            else:
                ax.set_visible(False)

        for fun in self._callbacks:
            fun(event, p)

    def get(self, x):
        return self._data.index(x)

    def remove(self):
        for ax in self._vax.values():
            if ax.axes is not None:
                ax.remove()

        for ax in self._hax.values():
            if ax.axes is not None:
                ax.remove()

        if self._date is not None:
            if self._date.axes is not None:
                self._date.remove()

    # 清空游標
    def clear(self):
        if self._date is not None:
            self._date.set_text('')

        for ax in self._vax.values():
            if ax.axes is not None:
                ax.remove()

        for ax in self._hax.values():
            if ax.axes is not None:
                ax.remove()

        self._vax.clear()
        self._hax.clear()


# K線
class Watch(SubAxes):
    text = {
        '日': name.DATE,
        '開': name.OPEN,
        '收': name.CLOSE,
        '高': name.HIGH,
        '低': name.LOW,
        '漲': name.INCREASE,
        '%': name.D_INCREASE,
        '量': name.VOLUME,
        '振': name.AMPLITUDE,
    }

    name = NAME

    x_text_offset = 0.7

    def __init__(self):
        SubAxes.__init__(self)
        self.info = None

    # 繪製主圖
    def plot(self, **kwargs):
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
    def plot_text(self, text, **kwargs):
        last = self._c_watch.get_last()
        for name, c in self.text.items():
            text.add(name, c, last[c], offset_x=self.x_text_offset)

    def plot_info(self):
        _y_tick = self.axes.yaxis.major.locator.tick
        _y_max = self.axes.yaxis.major.locator.get_ticks()[-1]

        self.info = self.axes.text(
            -1,
            _y_max + _y_tick / 2,
            self.stock_info(),
            fontsize=self.xy_font_size,
            color='white'
        )

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
            'marker_date': MarkerDate(),
            'range': Range(),
        }

    def _clear(self):
        if self.info is not None:
            self.info.set_text('')

        if len(self.axes.collections) > 0:
            self.axes.collections[0].remove()
            self.axes.collections[0].remove()


# 成交量
class Volume(SubAxes):
    # 紅k
    up_color = '#9A0000'

    # 黑k
    down_color = '#23B100'

    name = 'volume'

    master_name = NAME

    x_text_offset = 1.2

    def plot(self, **kwargs):
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

        self.axes.set_ylim(np.nanmin(volumes), 1.1 * np.nanmax(volumes))
        self.axes.bar(
            x_data,
            volumes,
            width=0.85,
            linewidth=mwidths._dfinterpolate(mwidths._widths, self._c_watch.range, 'vlw'),
            color=colors,
            ec=mplotting._adjust_color_brightness(colors, 0.90)
        )

        v_ma = self._c_watch.get_volume_ma([5])

        self.line[5] = self.axes.plot(
            np.arange(len(v_ma)),
            v_ma,
            linewidth=1.8
        )

        self._major(volumes)
        self._update_label()

    def plot_text(self, text, **kwargs):
        text.add('5vma', '5vma', self.line[5][0].get_ydata()[-1], color='#FF3399', offset_x=self.x_text_offset)

    def _major(self, volume):
        self.axes.yaxis.set_major_locator(VolumeLocator(volume, len=3))
        self.axes.yaxis.set_major_formatter(VolumeFormatter())

        for ticks in [self.axes.get_yticklabels(), self.axes.get_xticklabels()]:
            for tick in ticks:
                tick.update({'fontsize': self.xy_font_size, 'rotation': 0})

    def _clear(self):
        if len(self.axes.containers) > 0:
            self.axes.containers[0].remove()

        for name, line in self.line.items():
            line[0].remove()

        self.line.clear()


# 均線
class MA(SubAxes):
    # 顏色
    color = {
        2: '#999900',
        5: '#FF8000',
        10: '#00CCCC',
        20: '#00CC66',
        60: '#FFFF00',
        120: '#6600CC',
        240: '#CC00CC',
    }

    line_width = 1.8

    name = 'ma'

    master_name = NAME

    x_text_offset = 1.2

    def __init__(self):
        SubAxes.__init__(self)
        self.day = []

    def plot(self, **kwargs):
        day = kwargs.get('ma')

        if day is None:
            return

        self.day = day
        ma = self._c_watch.get_ma(day)

        for d in day:
            if d not in self.line:
                self._add(d, ma[f'{d}ma'])

        day = {d: '' for d in day}

        for d, v in self.line.items():
            if d not in day:
                v.remove()
                del self.line[d]

    def plot_text(self, text, **kwargs):
        for name, line in self.line.items():
            key = f'{name}ma'
            text.add(key, key, self.line[name][0].get_ydata()[-1], color=self.color[name], offset_x=self.x_text_offset)

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

        self.line[day] = line

        return line

    def _clear(self):
        for name, line in self.line.items():
            line[0].remove()

        self.line.clear()


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

    name = 'max_min'

    master_name = NAME

    def __init__(self):
        SubAxes.__init__(self)
        self._max = None
        self._min = None

    def plot(self, **kwargs):
        y_tick = self.axes.yaxis.major.locator.tick
        (x_max, y_max) = self._c_watch.get_xy_max()
        (x_min, y_min) = self._c_watch.get_xy_min()

        self._max = self._set(x_max, y_max, y_offset=(y_tick / 2))
        self._min = self._set(x_min, y_min, y_offset=-y_tick)

    def _set(self, x, y, y_offset=0.0):
        return self.axes.annotate(
            y,
            xy=(x, y),
            xytext=(x, y + y_offset),
            color='black',
            size=self.xy_font_size,
            arrowprops=dict(arrowstyle="simple"),
            bbox=dict(boxstyle='square', fc="0.5"),
            ha='center'
        )

    def _clear(self):
        if self._max is not None:
            self._max.remove()

        if self._min is not None:
            self._min.remove()


# 標示日期
class MarkerDate(SubAxes):
    name = 'marker_date'

    master_name = NAME

    def __init__(self):
        SubAxes.__init__(self)
        self._markerDate = None

    def plot(self, **kwargs):
        marker = kwargs.get('marker_date')

        if marker is None or len(marker) == 0:
            return

        dates = self._c_watch.date().tolist()
        close = self._c_watch.close().tolist()
        open = self._c_watch.open().tolist()
        y_data = np.full(len(dates), np.nan)

        for date in marker:
            index = dates.index(date)
            if close[index] > open[index]:
                y_data[index] = open[index] * 0.99
            else:
                y_data[index] = close[index] * 0.99

        self._markerDate = self.axes.scatter(np.arange(len(dates)), y_data, s=700, marker='^', color='#9933FF', alpha=1)

    def _clear(self):
        if self._markerDate is not None:
            self._markerDate.remove()
            self._markerDate = None


# 選取範圍
class Range(SubAxes):
    def __init__(self):
        SubAxes.__init__(self)
        self._rectangle = None

    def plot(self, **kwargs):
        range = kwargs.get('range')

        if len(range) <= 1:
            return

        if range[0] == '' or range[1] == '':
            return

        date = self._c_watch.date()
        range = date[(range[0] <= date) & (range[1] >= date)]

        if range.empty:
            return

        date = date.tolist()
        x1 = date.index(range[0])
        x2 = date.index(range[-1])
        self._rectangle = self.axes.add_patch(
            plt.Rectangle((x1 - 0.5, 0), (x2 - x1) + 1, 10000, color='#66FFFF', alpha=0.2, lw=4)
        )

    def _clear(self):
        if self._rectangle is not None:
            self._rectangle.remove()
            self._rectangle = None


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

        loc = list(monthFirstWorkDay.values())
        last = len(self.data) - 1

        if len(self.data) > 30:
            if last - loc[-1] < 5:
                del loc[-1]

            if loc[1] - loc[0] < 5:
                del loc[1]

            loc.append(last)

        self.loc = loc

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

        for i in range(30):
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
    def __init__(self, data, len=5):
        self.data = data
        self.len = len
        self.locs = []

    def __call__(self):
        return self.tick_values(None, None)

    def tick_values(self, vmin, vmax):
        if len(self.locs) > 0:
            return self.locs

        mx = self.data.max()
        mi = self.data.min()
        step = 10 ** (len(str(int((mx - mi) / 3))) - 1)
        diff = (mx - mi) / self.len
        step = int((diff - diff % step) + step)

        self.locs.append(0)

        for i in range(10):
            v = step * (i + 1)
            self.locs.append(v)

            if v > mx:
                break

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


# 交易量格式
class VolumeFormatter(mticks.Formatter):
    def __call__(self, x, pos=None):
        return self.format(x)

    def format(self, x):
        return '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (
                x * 1e-3) if x >= 1e3 else '%1.0f' % x
