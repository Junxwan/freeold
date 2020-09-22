# -*- coding: utf-8 -*-
import calendar
import logging
import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from . import query, name

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

COLUMNS = [OPEN, CLOSE, HIGH, LOW, INCREASE, AMPLITUDE, VOLUME]

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
        data = self.data.loc[code]
        q = data.loc[DATE]
        return data[q[q < date].index[0]]

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
                self.data = pd.merge(self.data, data, on=['code', 'name'], how='inner')

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

        ready = [
            os.path.basename(p).split('.')[0] for p in
            glob.glob(os.path.join(dir, f'{datetime.now().year}*.csv'))
        ]

        [self._stock.read(n) for n in sorted(ready, reverse=True)]

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

        c_data = pd.DataFrame([
            stock[i].tolist() for i in stock],
            columns=stock.index.tolist()
        )

        c_data[DATE] = pd.to_datetime(c_data[DATE])
        c_data = c_data.set_index(DATE).sort_index()
        c_data.insert(0, DATE, [t.strftime('%Y-%m-%d') for t in c_data.index])

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
            self._li = self._ri - self.range
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
                self.set(column, self._data[CLOSE].rolling(d).mean().round(2).values)

        return self.get().loc[:, [f'{d}ma' for d in day]]

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
        data = self.code(code, date)

        if data is None:
            return None

        if code not in self._date:
            self._date[code] = {}

        if date not in self._date[code]:
            self._date[code][date] = TrendData(code, data, tick=self.tick(code, data['0']['time'][:10]))

        return self._date[code][date]

    def read(self, date):
        if date not in self.data:
            file = os.path.join(self.trend_dir, date[:4], f'{date}.csv')

            if os.path.exists(file) == False:
                return None

            self.data[date] = pd.read_csv(file, index_col=[0, 1], header=[0], low_memory=False)

        return self.data[date]

    def now_date(self):
        return os.path.basename(
            glob.glob(os.path.join(self.trend_dir, str(datetime.now().year), '*.csv'))[-1]
        ).split('.')[0]


class TrendData():
    def __init__(self, code, data, tick=None):
        self.code = code
        self._data = data.dropna(axis='columns')
        self.date = data.loc['time'][0][:10]

        date_times = pd.date_range(start=f'{self.date} 09:00:00', end=f'{self.date} 13:33:00', freq='min')
        for i in range(4):
            date_times = date_times.delete(266)

        self.times = {t.strftime('%H:%M:%S'): i for i, t in enumerate(date_times)}

        self._format()
        self._format_tick(tick)

    def _format(self):
        data = self._data.dropna(axis='columns').copy()
        data.loc[VOLUME] = self._data.loc[VOLUME].astype(int)
        data.loc['price'] = self._data.loc['price'].astype(float)
        data.loc['time'] = self._data.loc['time'].transform(lambda x: x[11:])
        data.columns = self._data.columns.astype(int)
        self._data = data

    def _format_tick(self, tick):
        avg = []

        if tick is None:
            avg = np.full([1, len(self._data.loc['time'])], np.nan).tolist()[0]
        else:
            q = tick['time']
            times = list(self.times)

            for i, time in enumerate(times[1:-4]):
                d = tick[q.between(times[i], time)]

                if d.empty:
                    if len(avg) == 0:
                        avg.append(tick.loc[0]['buy'])
                    else:
                        avg.append(avg[-1])
                else:
                    avg.append(d.dropna().iloc[-1]['avg'])

            avg.append(avg[-1])
            pd.DataFrame([avg], index=['avg'])

        self._data = self._data.append(pd.DataFrame([avg], index=['avg']))

    def value(self):
        return self._data

    def time(self):
        return self._data.loc['time'].dropna()

    def price(self):
        return self._data.loc['price']

    def volume(self):
        return self._data.loc[VOLUME]

    def tick(self):
        return self._data.loc['avg']

    def first(self):
        return self._data[0]


class Query():
    q = {
        'weak': query.WeaK(),
        'open_high_close_low': query.OpenHighCloseLow()
    }

    def __init__(self, csv_dir):
        self._stock = Stock(os.path.join(csv_dir, 'stock'))
        self._trend = Trend(csv_dir)

    def run(self, name, start, end=None, output=None, codes=None):
        stock = self._stock.date(start, end)
        query = self.q[name]

        if stock.empty:
            logging.info(f'======= not data for {start} to {end} =======')
            return

        if codes == None:
            codes = stock.index.levels[0]

        logging.info(f'======= exec {name} =======')

        columns = COLUMNS.copy()
        columns.insert(0, 'code')
        columns.insert(1, 'name')

        if stock.ndim == 1:
            stock = pd.DataFrame(stock)

        for i, index in enumerate(stock.columns):
            result = []
            date = stock[index].iloc[0]

            for code in codes:
                value = stock.loc[code].iloc[:, i:]

                logging.info(f"exec code: {code} date: {date}")

                if query.run(value, self._trend.code(code, date)):
                    d = value[index][1:].tolist()
                    d.insert(0, code)
                    d.insert(1, self._stock.info(code)['name'])
                    result.append(d)

            frame = pd.DataFrame(result, columns=columns)
            frame = query.sort(frame)
            frame = query.limit(frame)

            if (output != None) & (os.path.exists(output) == True):
                dir = os.path.join(output, date[:4] + date[5:7])

                if os.path.exists(dir) == False:
                    os.mkdir(dir)

                logging.info(f'======= save {name} - {date} =======')

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
