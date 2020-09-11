# -*- coding: utf-8 -*-

import logging
import os
import glob
from datetime import datetime

import pandas as pd
import numpy as np

# 日期
DATE = 'date'

# 開盤價
OPEN = 'open'

# 收盤價
CLOSE = 'close'

# 最高價
HIGH = 'high'

# 最低價
LOW = 'low'

# 漲幅
INCREASE = 'increase'

# 震幅
AMPLITUDE = 'amplitude'

# 成交量
VOLUME = 'volume'

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


class stock():
    data = pd.DataFrame()
    stock = pd.DataFrame()
    tick = pd.DataFrame()
    csv = []
    dk = {}

    def __init__(self, dir):
        self.dir = dir

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

    def readAll(self):
        for dk, path in self.csv.items():
            if dk not in self.dk:
                self.read(os.path.basename(path).split('.')[0])

    def read(self, dk):
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

        return self.data.iloc[:, int(r.index[0]):(r.index[-1])]

    def code(self, code):
        return self.stock[self.stock['code'] == code].iloc[0]

    def dates(self):
        self.readAll()
        return self.qDate().to_numpy().tolist()

    def afterDates(self, date):
        self.readAll()
        q = self.qDate()
        r = q[q <= date]
        return self.data.iloc[0, int(r.index[0]):(r.index[-1])].to_numpy().tolist()

    def qDate(self):
        return self.data.loc[2330].loc[DATE]

    def run(self, query, start, end=None, output=None, codes=None):
        data = self.date(start, end)

        if data.empty:
            logging.info(f'======= not data for {start} to {end} =======')
            return

        if codes == None:
            codes = data.index.levels[0]

        logging.info(f'======= exec {query.name} =======')

        columns = COLUMNS.copy()
        columns.insert(0, 'code')
        columns.insert(1, 'name')

        if data.ndim == 1:
            data = pd.DataFrame(data)

        for i, index in enumerate(data.columns):
            result = []
            date = data[index].iloc[0]

            for code in codes:
                value = data.loc[code]
                v = value.iloc[:, i:]

                logging.info(f"exec code: {code} date: {date}")

                if query.exec(v):
                    d = v[index][1:].tolist()
                    d.insert(0, code)
                    d.insert(1, self.code(code)['name'])
                    result.append(d)

            frame = pd.DataFrame(result, columns=columns)

            if query.sort != '':
                frame = frame.sort_values(by=query.sort, ascending=query.asc)

            if query.num > 0:
                frame = frame[:query.num]

            if (output != None) & (os.path.exists(output) == True):
                dir = os.path.join(output, date[:4] + date[5:7])

                if os.path.exists(dir) == False:
                    os.mkdir(dir)

                logging.info(f'======= save {query.name} - {date} =======')

                frame.to_csv(os.path.join(dir, date) + '.csv', index=False, encoding='utf_8_sig')


class Watch():
    def __init__(self, dir, ready=None):
        self._dir = dir
        self._stock = stock(dir)

        if ready == None:
            self._stock.readAll()
        elif type(ready) == list:
            [self._stock.read(n) for n in ready]
        else:
            self._stock.read(ready)

        self._data = {}

    def code(self, code, range=60, date=None):
        if code not in self._data:
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
            self._data[code] = WatchData(code, c_data)

        self._data[code].set_range(range)

        try:
            if date != None:
                date = datetime.fromisoformat(date)
                self._data[code].set_date(date.strftime('%Y-%m-%d'))
        except:
            pass

        return self._data[code]

    def info(self, code):
        return self._stock.code(code)


class WatchData():
    def __init__(self, code, data):
        self.code = code
        self._data = data
        self.range = 60
        self._li = 0
        self._ri = data.shape[0]

    def set_range(self, num):
        self.range = num
        self._li = self._ri - self.range

    def set_date(self, date):
        self._ri = self._data.index.get_loc((self._data[DATE] == date).idxmax()) + 1
        self._li = self._ri - self.range

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
