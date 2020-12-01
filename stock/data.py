# -*- coding: utf-8 -*-
import calendar
import logging
import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from . import query, name, weak, pattern

# 日期
DATE = name.DATE

# 開盤價
OPEN = name.OPEN

# 收盤價
CLOSE = name.CLOSE

# 最高價
HIGH = name.HIGH

# 最低價
LOW = name.LOW

# 漲幅
INCREASE = name.INCREASE

# 震幅
AMPLITUDE = name.AMPLITUDE

# 成交量
VOLUME = name.VOLUME

COLUMNS = [OPEN, CLOSE, HIGH, LOW, INCREASE, name.D_INCREASE, AMPLITUDE, VOLUME]

# 個股基本資料
INFO_FILE_NAME = 'stock'

STOCK_COLUMNS = [
    'code',
    'name',
    'value',
    'industry',
    'group',
    'revenue',
    'product',
    'use',
    'concept',
    'title',
    'remarks',
    'on',
    'status'
]

_tick_level = [50, 25, 10, 7.5, 5, 2.5, 1, 0.5, 0.25, 0.1, 0.05]


# 股價tick
def get_tick(close):
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
def get_len(close):
    if close < 50:
        return 2
    elif close < 500:
        return 1

    return 0


# 漲停價
def get_max(close):
    # 漲停價為昨日收盤價上漲10%
    max = round(close * 1.1, get_len(close))
    mc = close

    # 由於漲幅會受到股價不同區間而tick不同，
    # 所以在計算股價時如果有跨區間時tick不同會造成計算漲幅超過10%
    # 如昨日收盤價51.2，跌停為46.1，漲停為56.3，但tick跨越0.05跟0.1
    # 到了50元股價就不能用0.05來計算否則會超過10%限制
    while True:
        t = get_tick(mc)

        if max <= mc:
            if round((((mc / close) - 1) * 100), 2) > 10:
                max = mc - t

            max = round(max, get_len(max))
            break

        mc = mc + t
        mc = round(mc, get_len(mc))

    return max


# 跌停價
def get_min(close):
    # 跌停價為昨日收盤價下跌10%
    min = round(close * 0.9, get_len(close))
    mc = close

    # 由於漲幅會受到股價不同區間而tick不同，
    # 所以在計算股價時如果有跨區間時tick不同會造成計算漲幅超過10%
    # 如昨日收盤價51.2，跌停為46.1，漲停為56.3，但tick跨越0.05跟0.1
    # 到了50元股價就不能用0.05來計算否則會超過10%限制
    while True:
        t = get_tick(mc)

        if min >= mc:
            if round(((mc / close) - 1) * -100, 2) > 10:
                min = mc + t

            min = round(min, get_len(min))
            break

        mc = mc - t
        mc = round(mc, get_len(mc))

    return min


# 該股價區間的y軸價格
def tick(y_max, y_min):
    diff = y_max - y_min
    tick = _tick_level[0]

    for i, t in enumerate(_tick_level):
        d = (diff / t)
        if d > 10:
            tick = t
            break
    return tick


# 該股價區間所有y軸價格
def ticks(y_max, y_min):
    diff = y_max - y_min
    tick = _tick_level[0]

    for i, t in enumerate(_tick_level):
        d = (diff / t)
        if d > 10:
            tick = t
            break

    start = (y_min - (y_min % tick)) - tick
    ticks = []

    for i in range(30):
        p = start + (tick * i)
        ticks.append(start + (tick * i))

        if p > y_max:
            ticks.insert(0, start - tick)
            ticks.append(p + tick)
            break

    return ticks


class Stock():
    data = pd.DataFrame()
    stock = pd.DataFrame()
    csv = []

    def __init__(self, dir):
        self.dir = dir
        self.dk = {}

        if self.stock.empty:
            self.stock = pd.read_csv(os.path.join(dir, INFO_FILE_NAME) + '.csv')
            self.stock.columns = STOCK_COLUMNS

        self.csv = {
            os.path.basename(f).split('.')[0]: f
            for f in sorted(glob.glob(os.path.join(self.dir, '20*.csv')), reverse=True)
        }

    def year(self, year):
        return self.query(f"{year}-01-01", f"{year}-12-31")

    def month(self, m):
        return self.query(f"{m[:4]}-{m[4:6]}-01", f"{m[:4]}-{m[4:6]}-31")

    def date(self, start, end=None):
        if start.__len__() == 4:
            if (end == None) | (end == ''):
                return self.year(start)
            elif end.__len__() == 4:
                return self.query(f"{start}-01-01", f"{end}-12-31")
            else:
                return self.query(f"{start}-01-01", end)
        elif (end == None) | (end == ''):
            return self.query(start)
        elif end.__len__() == 4:
            return self.query(start, f"{end}-12-31")

        return self.query(start, end)

    def yesterday(self, code, date):
        if code not in self.data.index.levels[0]:
            return None

        data = self.data.loc[code]
        q = data.loc[DATE]
        q = q[q < date]

        if q.empty:
            return None

        return data[q.index[0]]

    def readAll(self):
        for dk, path in self.csv.items():
            if dk not in self.dk:
                self.read(os.path.basename(path).split('.')[0])

    def read(self, dk):
        dk = str(dk)
        if dk not in self.dk:
            data = pd.read_csv(os.path.join(self.dir, f'{dk}.csv'), index_col=[0, 1], header=[0])

            # 將除了DATE以外的index value 字串轉為float
            pIndex = pd.IndexSlice[:, data.index.levels[1].copy().drop(DATE).tolist()]
            data.loc[pIndex, :] = data.loc[pIndex, :].astype(float)

            if self.data.empty:
                self.data = data
                self.data.columns = np.arange(0, data.columns.size)
            else:
                data.columns = np.arange(self.data.columns.size, self.data.columns.size + data.columns.size)
                self.data = pd.merge(self.data, data, on=['code', 'name'], how='outer')

            logging.info(f'read price for date: {dk}')

            self.dk[dk] = True

    def query(self, start, end=None):
        self.readAll()

        q = self.qDate()

        if end == None:
            r = q[start == q]
            if r.empty:
                return r
            return self.data.iloc[:, r.index[0]]

        if end == False:
            r = q[start >= q]
        else:
            r = q[(start <= q) & (end >= q)]

        if r.empty:
            return r

        return self.data.iloc[:, int(r.index[0]):(r.index[-1]) + 1]

    def info(self, code):
        return self.stock[self.stock['code'] == code].iloc[0]

    def dates(self):
        self.readAll()
        return self.qDate().to_numpy().tolist()

    def afterDates(self, date):
        self.readAll()
        q = self.qDate()
        r = q[q <= date]
        return self.data.iloc[0, int(r.index[0]):(r.index[-1])].to_numpy().tolist()

    def qDate(self, code=2330):
        return self.data.loc[code].loc[DATE]


class Dealer():
    def __init__(self, dir):
        self._data = {}
        data = []
        master = ''

        for index, rows in pd.read_csv(os.path.join(dir, 'dealer.csv')).iterrows():
            names = rows[1].split('-')
            names[0] = names[0].strip()

            if len(names) > 1:
                rows[1] = f'{names[0]}-{names[1].strip()}'
            else:
                rows[1] = names[0]
                master = rows[0]

            rows = rows.tolist()
            rows.append(master)
            data.append(rows)

        self._data = pd.DataFrame(
            data,
            columns=['code', 'name', 'open_date', 'address', 'iphone', 'master']
        )

    def code(self, code):
        d = self._data[self._data['code'] == code]

        if d.empty:
            return None

        return d.iloc[0]

    def name(self, name):
        d = self._data[self._data['name'] == name]

        if d.empty:
            return None

        return d.iloc[0]

    def group_code(self):
        group = {}
        for code, rows in self._data.groupby('master'):
            group[code] = rows['code'].tolist()

        return group


class K():
    def __init__(self, dir):
        self._dir = dir
        self._stock = Stock(dir)
        self._stock.readAll()
        # year = datetime.now().year

        # ready = [
        #     os.path.basename(p).split('.')[0] for p in
        #     glob.glob(os.path.join(dir, f'{year}*.csv'))
        # ]
        #
        # ready.insert(0, f'{year - 1}')
        #
        # [self._stock.read(n) for n in sorted(ready, reverse=True)]

        self._data = {}
        self._k_data = {}

    def code(self, code, range=60, date=None):
        if code not in self._data:
            c_data = self._code(code)

            if c_data is None:
                return None

            self._data[code] = c_data

        self._data[code].set_range(range)

        try:
            if date != None:
                date = datetime.fromisoformat(date)
                s_date = date.strftime('%Y-%m-%d')
                if self._data[code].isDate(date):
                    if self._data[code].set_date(s_date) == False:
                        return None
                else:
                    self._stock.read(date.year)
                    c_data = self._code(code)
                    c_data.set_range(range)
                    c_data.set_date(s_date)
                    self._data[code] = c_data
        except:
            return None

        return self._data[code]

    def _code(self, code):
        try:
            stock = self._stock.data.loc[code]
        except:
            return None

        c_data = pd.DataFrame(
            [stock[i].tolist() for i in stock],
            columns=stock.index.tolist()
        ).dropna(axis='index', how='all')

        c_data[DATE] = pd.to_datetime(c_data[DATE])
        c_data = c_data.set_index(DATE).sort_index()
        c_data.insert(0, DATE, [t.strftime('%Y-%m-%d') for t in c_data.index.dropna()])

        if code not in self._k_data:
            self._k_data[code] = KData(code, c_data)

        return self._k_data[code]

    def info(self, code):
        return self._stock.info(code)

    def get_stock(self):
        return self._stock


class KData():
    def __init__(self, code, data):
        self.code = code
        self._data = data
        self.range = 60
        self._li = 0
        self._ri = data.shape[0]
        self._start_date = data.index[0]

    def set_range(self, num):
        self.range = num
        self._li = self._ri - self.range

    def set_date(self, date):
        try:
            self._ri = self._data.index.get_loc(date) + 1
            if self._ri > self.range:
                self._li = self._ri - self.range
            else:
                self._li = 0
        except:
            return False

        return True

    def isDate(self, date):
        return self._start_date <= date

    # 日期
    def date(self):
        return self.get(column=DATE)

    # 開盤
    def open(self):
        return self.get(column=OPEN)

    # 收盤
    def close(self):
        return self.get(column=CLOSE)

    # 最高價
    def high(self):
        return self.get(column=HIGH)

    # 最低價
    def low(self):
        return self.get(column=LOW)

    # 成交量
    def volume(self):
        return self.get(column=VOLUME)

    def set(self, column, value):
        self._data.loc[:, column] = value

    def index(self, index):
        return self.get().iloc[index]

    def get(self, column=None):
        d = self._data[self._li:self._ri]

        if column == None:
            return d

        return d[column]

    def get_last(self):
        return self.get().iloc[-1]

    # 均線
    def get_ma(self, day):
        for d in day:
            if f'{d}ma' not in self._data:
                column = f'{d}ma'
                self.set(column, self._data[name.CLOSE].rolling(d).mean().round(2).values)

        return self.get().loc[:, [f'{d}ma' for d in day]]

    # 成交量均線
    def get_volume_ma(self, day):
        for d in day:
            if f'{d}vma' not in self._data:
                column = f'{d}vma'
                self.set(column, self._data[name.VOLUME].rolling(d).mean().round(2).values)

        return self.get().loc[:, [f'{d}vma' for d in day]]

    # 最高xy座標
    def get_xy_max(self):
        return self.get_x_max(), self.get_y_max()

    # 最低xy座標
    def get_xy_min(self):
        return self.get_x_min(), self.get_y_min()

    # x座標 最高與最低
    def get_x_max_min(self):
        return self.get_x_max(), self.get_x_min()

    # y座標 最高與最低
    def get_y_max_min(self):
        return self.get_y_max(), self.get_y_min()

    # 最高x座標
    def get_x_max(self):
        d = self.get()
        return d.index.get_loc(d[HIGH].idxmax())

    # 最低x座標
    def get_x_min(self):
        d = self.get()
        return d.index.get_loc(d[LOW].idxmin())

    # 最高y座標
    def get_y_max(self):
        return self.high().max()

    # 最低y座標
    def get_y_min(self):
        return self.low().min()


class Trend():
    data = {}
    ticks = {}
    dk = {}
    _date = {}

    def __init__(self, dir):
        self.trend_dir = os.path.join(dir, 'trend', 'stock')
        self.tick_dir = os.path.join(dir, 'tick')

    def month(self, month):
        dates = [
            os.path.basename(p).split('.')[0] for p in
            glob.glob(os.path.join(self.trend_dir, month[:4], f'{month[:4]}-{month[4:6]}-*.csv'))
        ]

        data = {}
        for date in dates:
            data[date] = self.read(date)

        return data

    def date(self, date):
        self.read(date)

    def tick(self, code, date):
        if date in self.ticks:
            if code in self.ticks[date]:
                return self.ticks[date][code]

        tick_file = os.path.join(self.tick_dir, date, str(code)) + '.csv'

        if os.path.exists(tick_file):
            if date not in self.ticks:
                self.ticks[date] = {}

            if code not in self.ticks[date]:
                self.ticks[date][code] = pd.read_csv(tick_file)

            return self.ticks[date][code]

        return None

    def code(self, code, date):
        if len(self.data) > 30:
            self.data = {}

        if date is None:
            date = self.now_date()

        self.read(date)
        if date not in self.data:
            return None

        try:
            return self.data[date].loc[int(code)]
        except KeyError:
            return None

    def get(self, code, date):
        if code not in self._date:
            self._date[code] = {}

        if date not in self._date[code]:
            data = self.code(code, date)

            if data is None:
                return None

            self._date[code][date] = TrendData(code, data)

        return self._date[code][date]

    def read(self, date):
        if date not in self.data:
            file = self.file_name(date)

            if os.path.exists(file) == False:
                return None

            self.data[date] = pd.read_csv(file, index_col=[0, 1], header=[0], low_memory=False)

        return self.data[date]

    def now_date(self):
        return os.path.basename(
            sorted(glob.glob(os.path.join(self.trend_dir, str(datetime.now().year), '*.csv')), reverse=True)[0]
        ).split('.')[0]

    def file_name(self, date):
        return os.path.join(self.trend_dir, date[:4], f'{date}.csv')


class TrendData():
    def __init__(self, code, data):
        self.code = code
        self._data = data.dropna(axis='columns', how='all')
        self.date = data.loc[name.TIME][0][:10]
        self._x = []
        self._y = []
        self._y_volume = []
        self._y_max = 0
        self._x_max = 0
        self._y_min = 0
        self._x_min = 0
        self._x_pos = []

        date_times = pd.date_range(start=f'{self.date} 09:00:00', end=f'{self.date} 13:33:00', freq='min')
        for i in range(4):
            date_times = date_times.delete(266)

        self.times = {t.strftime('%H:%M:%S'): i for i, t in enumerate(date_times)}

        self._format()

    def _format(self):
        data = self._data.copy()
        data.loc[VOLUME] = self._data.loc[VOLUME].astype(int)
        data.loc[name.CLOSE] = self._data.loc[name.CLOSE].astype(float)
        data.loc[name.HIGH] = self._data.loc[name.HIGH].astype(float)
        data.loc[name.LOW] = self._data.loc[name.LOW].astype(float)
        data.loc[name.AVG] = self._data.loc[name.AVG].astype(float)
        data.loc[name.OPEN] = self._data.loc[name.OPEN].astype(float)
        data.loc[name.PRICE] = self._data.loc[name.PRICE].astype(float)
        data.loc[name.PRICE_1] = self._data.loc[name.PRICE_1].astype(float)
        data.loc[name.TIME] = self._data.loc[name.TIME].transform(lambda x: x[11:])
        data.columns = self._data.columns.astype(int)
        self._data = data
        self.values = {v['time']: v for i, v in data.to_dict().items()}

    def value(self):
        return self._data

    def time(self):
        return self._data.loc[name.TIME]

    def high(self):
        return self._data.loc[name.HIGH]

    def low(self):
        return self._data.loc[name.LOW]

    def avg(self):
        return self._data.loc[name.AVG]

    def open(self):
        return self._data.loc[name.OPEN]

    def close(self):
        return self._data.loc[name.CLOSE]

    def volume(self):
        return self._data.loc[name.VOLUME]

    def first(self):
        return self._data[0]

    def x(self) -> list:
        if len(self._x) > 0:
            return self._x

        x_lim = self.x_lim()
        self._x = [x_lim[0], 0]

        for i, t in enumerate(self.time()):
            if pd.isna(self.values[t][name.PRICE_1]) == False:
                self._x.append(self.times[t])

            self._x.append(self.times[t])

        return self._x

    def y(self, close=0) -> list:
        if len(self._y) > 0:
            return self._y

        self._y = [close, close]

        for i, t in enumerate(self.time()):
            self._y.append(self.values[t][name.PRICE])

            if pd.isna(self.values[t][name.PRICE_1]) == False:
                self._y.append(self.values[t][name.PRICE_1])

        return self._y

    def x_lim(self):
        # 09:00為0，08:55 ~ 13:33
        return -5, len(self.times)

    def x_max(self):
        if self._x_max == 0:
            self._x_max = self.times[self.time()[(self.high() == self.y_max())].iloc[0]]

        return self._x_max

    def x_min(self):
        if self._x_min == 0:
            self._x_min = self.times[self.time()[self.low() == self.y_min()].iloc[0]]

        return self._x_min

    def y_max(self):
        if self._y_max == 0:
            self._y_max = self.high().max()
        return self._y_max

    def y_min(self):
        if self._y_min == 0:
            self._y_min = self.low().min()
        return self._y_min

    def y_volume(self):
        if len(self._y_volume) == 0:
            self._y_volume = [0, 0]

            for i, t in enumerate(self.time()):
                self._y_volume.append(self.values[t][name.VOLUME])

                if pd.isna(self.values[t][name.PRICE_1]) == False:
                    self._y_volume.append(self.values[t][name.VOLUME])

        return self._y_volume

    def x_pos(self):
        # 09:00 10:00 11:00 12:00 13:00
        if len(self._x_pos) == 0:
            l = 60
            self._x_pos = [l * i for i in range(5)]

        return self._x_pos


class Query():
    q = {
        'weak': weak.LIST,
        'pattern': pattern.LIST,
    }

    def __init__(self, csv_dir, stock=None):
        if stock is None:
            self._stock = Stock(os.path.join(csv_dir, 'stock'))
        else:
            self._stock = stock

        self._trend = Trend(csv_dir)

    def run(self, start, strategy, end=None, codes=None, is_save=True):
        name = os.path.normcase(strategy).split('strategy' + os.path.sep)[1]
        q = name.split(os.path.sep)
        query = self.q[q[-2]]
        if len(q) >= 2:
            query = query[q[-1]]

        query.trendQ = self._trend
        query.stockQ = self._stock

        if end is None or end == '':
            stock = self._stock.query(start, False)
        else:
            stock = self._stock.query(end, False)

        if stock.empty:
            logging.info(f'======= not data for {start} to {end} =======')
            return

        if codes is None or codes == '':
            codes = stock.index.levels[0]
        elif os.path.isdir(codes):
            codes = {
                os.path.basename(path).split('.')[0]: path for path in
                glob.glob(os.path.join(codes, '*', '*.csv'))
            }
        elif type(codes) == str:
            codes = [int(codes)]

        logging.info(f'======= exec {name} =======')

        if stock.ndim == 1:
            stock = pd.DataFrame(stock)

        if end is None or end == '':
            range = enumerate([stock.columns[0]])
        else:
            ds = stock.loc[2330].loc['date']
            range = enumerate(ds[(ds >= start) & (end >= ds)].index)

        data = dict()
        for index_day, index in range:
            result = []
            date = stock[index].iloc[0]

            if type(codes) == dict:
                if date not in codes:
                    raise ValueError(f'codes is not {date}')
                cs = pd.read_csv(codes[date])['code']
            else:
                cs = codes

            for code in cs:
                value = stock.loc[code].iloc[:, index_day:].dropna(axis=1)

                if value.empty or value.columns[0] != index:
                    continue

                logging.info(f"exec code: {code} date: {date}")

                r = query.execute(
                    index,
                    code,
                    value,
                    self._stock.info(code)
                )

                if r is not None:
                    result.append(r)

            frame = pd.DataFrame(result, columns=query.columns())
            frame = query.sort(frame)
            frame = query.limit(frame)

            if is_save:
                self._toCsv(frame, date, strategy)
            else:
                data[date] = frame

            logging.info(f'{name} - {date} - {len(frame)}')

        return data

    def _toCsv(self, frame, date, output):
        dir = os.path.join(output, date[:4] + date[5:7])

        if os.path.exists(dir) == False:
            os.mkdir(dir)

        frame.to_csv(os.path.join(dir, date) + '.csv', index=False, encoding='utf_8_sig')


def calendar_xy(date, year=None, month=None):
    dateT = datetime.fromisoformat(date)

    if month is None:
        month = datetime.now().month

    if year is None:
        year = datetime.now().year

    prevMonth = 0
    dayX = 1
    dayY = dateT.isocalendar()[1] % 6

    if year != dateT.year:
        prevMonth += ((year - dateT.year) * 12)

    if month != dateT.month:
        prevMonth += abs(month - dateT.month)

    if dateT.isocalendar()[2] != 7:
        dayX = dateT.isocalendar()[2] + 1

    weeks = calendar.Calendar(calendar.SUNDAY).monthdayscalendar(dateT.year, dateT.month)

    for index in range(weeks.__len__()):
        if dateT.day in weeks[index]:
            dayY = index + 1

    return prevMonth, dayX, dayY
