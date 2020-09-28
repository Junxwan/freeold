# -*- coding: utf-8 -*-
import math
import matplotlib.ticker as mticks
from . import k
from stock import data, name

NAME = 'trend'


# 日內走勢
class Watch(k.SubAxes):
    text = {
        '時': name.TIME,
        '成': name.PRICE,
        '量': name.VOLUME,
    }

    name = NAME

    x_text_offset = 0.5

    # 繪製主圖
    def plot(self, **kwargs) -> bool:
        close = self._close()
        if close is None:
            return False

        self._major(close)

        x_lim = self._c_watch.x_lim()
        self.axes.set_xlim(x_lim[0], x_lim[1])
        self.axes.set_ylim(self.price_loc.min, self.price_loc.max)
        self.axes.axhline(y=(close), color='#335867')
        self.axes.grid(True)
        self.axes.name = name.PRICE

        self._plot_trend(close)
        self._update_label()

        return True

    def _plot_trend(self, close):
        self.axes.plot(self._c_watch.x(), self._c_watch.y(close), color='#FFFF00')

    def plot_text(self, text, **kwargs):
        text.add('日', 'date', self._c_watch.date, offset_x=self.x_text_offset)

        first = self._c_watch.first()
        for name, c in self.text.items():
            text.add(name, c, first[c], offset_x=self.x_text_offset)

    def plot_info(self):
        _y_max = self.axes.yaxis.major.locator.max
        _y_tick = self.axes.yaxis.major.locator.get_tick(_y_max)

        self.info = self.axes.text(
            -1,
            _y_max + _y_tick * 2,
            self.stock_info(),
            fontsize=self.xy_font_size,
            color='white'
        )

    def _close(self):
        yesterday = self._watch.yesterday(self.code, self._c_watch.date)
        if yesterday is None:
            return None

        return yesterday[data.CLOSE]

    def _major(self, close):
        self.axes.xaxis.set_major_locator(TimeLocator(self._c_watch))
        self.axes.xaxis.set_major_formatter(TimeFormatter())

        self.price_loc = PriceLocator(close)
        self.axes.yaxis.set_major_locator(self.price_loc)
        self.axes.yaxis.set_major_formatter(PriceFormatter(close))

    # 副圖
    def _sup_axes(self):
        return {
            'max_min': MaxMin(),
            name.AVG: Avg(),
        }

    def _update_label(self):
        self.axes.tick_params(axis='y', labelsize=self.xy_font_size, labelcolor='#FFFFFF')
        self.axes.tick_params(axis='x', labelsize=self.xy_font_size)

        y_label = self.axes.get_yticklabels()
        y_label[0].set_bbox(dict(facecolor='green'))
        y_label[-1].set_bbox(dict(facecolor='red'))
        close_pos = int(len(y_label) / 2)

        for l in y_label[1:close_pos]:
            l.set_color('#51F069')
            l.set_bbox(None)

        for l in y_label[close_pos + 1:-1]:
            l.set_color('#FF0000')
            l.set_bbox(None)

    def _clear(self):
        for i in range(len(self.axes.lines)):
            self.axes.lines[0].remove()


# 成交量
class Volume(k.SubAxes):
    name = name.VOLUME

    master_name = NAME

    def plot(self, **kwargs) -> bool:
        self.axes.name = self.name
        self.axes.grid(True)
        self.axes.set_ylim(0, 1.1 * self._c_watch.volume().max())
        self.axes.bar(self._c_watch.x(), self._c_watch.y_volume(), color='#FF00FF', width=0.2)

        self._major()
        self._update_label()

        return True

    def _major(self):
        self.axes.xaxis.set_major_locator(TimeLocator(self._c_watch))
        self.axes.xaxis.set_major_formatter(TimeFormatter())
        self.axes.yaxis.set_major_locator(k.VolumeLocator(self._c_watch.volume()))
        self.axes.yaxis.set_major_formatter(k.VolumeFormatter())

    def _update_label(self):
        self.axes.tick_params(axis='y', labelsize=self.xy_font_size)
        self.axes.tick_params(axis='x', labelsize=self.xy_font_size, labelcolor='#FFFF00')

    def _clear(self):
        if len(self.axes.containers) > 0:
            self.axes.containers[0].remove()


# 最高價與最低價
class MaxMin(k.SubAxes):
    name = 'max_min'

    master_name = NAME

    def __init__(self):
        k.SubAxes.__init__(self)
        self._max = None
        self._min = None

    def plot(self, **kwargs) -> bool:
        y_max = self._c_watch.y_max()
        x_max = self._c_watch.x_max()
        y_min = self._c_watch.y_min()
        x_min = self._c_watch.x_min()
        tick = self.axes.yaxis.major.locator.get_tick(y_min)

        y_max_text = y_max + (tick * 6)
        y_min_text = y_min - (tick * 6)

        if y_max_text >= self.axes.yaxis.major.locator.ticks[-1]:
            y_max_text = y_max - (tick * 10)

        if y_min_text <= self.axes.yaxis.major.locator.ticks[0]:
            y_min_text = y_min + (tick * 10)

        self._max = self.axes.annotate(
            y_max,
            xy=(x_max, y_max),
            xytext=(x_max, y_max_text),
            color='#FF0000',
            size=self.xy_font_size,
            arrowprops=dict(arrowstyle="simple", color='#FF0000'),
            ha="center", va="top"
        )

        self._min = self.axes.annotate(
            y_min,
            xy=(x_min, y_min),
            xytext=(x_min, y_min_text),
            color='#51F069',
            size=self.xy_font_size,
            arrowprops=dict(arrowstyle="simple", color='#51F069'),
            ha="center", va="top"
        )

        return True

    def _clear(self):
        if self._max is not None:
            self._max.remove()

        if self._min is not None:
            self._min.remove()


class Avg(k.SubAxes):
    name = name.AVG

    master_name = NAME

    def __init__(self):
        k.SubAxes.__init__(self)
        self.line = None

    def plot(self, **kwargs) -> bool:
        tick = self._c_watch.avg().tolist()
        y = self._c_watch.y()
        tick.insert(0, y[0])
        tick.insert(1, y[1])

        self.line = self.axes.plot(self._c_watch.x(), tick, linewidth=1, color='#22AC38')
        return True

    def _clear(self):
        if self.line is not None:
            self.line[0].remove()
            self.line = None


# 日內走勢事件
class MoveEvent(k.MoveEvent):
    def set_data(self, c_watch):
        self._c_watch = c_watch
        self._data = self._c_watch.value()

    def get(self, x):
        if self._c_watch.freq == 'm':
            times = [v for v in self._c_watch.times]

            for i, b in enumerate((self._data.loc[name.TIME] == times[x])):
                if b:
                    return self._data[i]
        else:
            h = int(x / 3600) + 9
            ms = int(x % 3600) / 60
            m = int(ms)
            s = int((ms - m) * 60)

            if h < 10:
                h = f'0{h}'

            if m < 10:
                m = f'0{m}'

            if s < 10:
                s = f'0{s}'

            data = self._data[self._c_watch.time() <= f'{h}:{m}:{s}']
            if data.empty == False:
                return data.iloc[-1]

        return None


# 日期塞選
class TimeLocator(mticks.Locator):
    def __init__(self, c_watch):
        mticks.Locator.__init__(self)
        self.c_watch = c_watch

    def __call__(self):
        return self.c_watch.x_pos()


# 日期格式
class TimeFormatter(mticks.Formatter):
    date = {
        0: 9,
        1: 10,
        2: 11,
        3: 12,
        4: 13,
    }

    def __call__(self, x, pos=None):
        return self.date[pos]


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
