import logging
import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime

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
    dk = {}

    def __init__(self, dir):
        self.dir = dir

        if self.stock.empty:
            self.stock = pd.read_csv(os.path.join(dir, INFO_FILE_NAME) + '.csv')
            self.stock.columns = STOCK_COLUMNS

    def year(self, year):
        for path in sorted(glob.glob(os.path.join(self.dir, f'{year}*.csv')), reverse=True):
            self.read(os.path.basename(path).split('.')[0])

        return self.query(f"{year}-01-01", f"{year}-12-31")

    def month(self, m):
        if int(m[:4]) != datetime.now().year:
            self.read(m[:4])
        else:
            self.read(m)

        return self.query(f"{m[:4]}-{m[4:6]}-01", f"{m[:4]}-{m[4:6]}-31")

    def date(self, date):
        if int(date[:4]) != datetime.now().year:
            self.read(date[:4])
        else:
            self.read(f'{date[:4]}{date[5:7]}')

        return self.query(date)

    def readAll(self):
        for path in sorted(glob.glob(os.path.join(self.dir, '20*.csv')), reverse=True):
            self.read(os.path.basename(path).split('.')[0])

    def read(self, dk):
        if dk not in self.dk:
            data = pd.read_csv(os.path.join(self.dir, f'{dk}.csv'), index_col=[0, 1], header=[0])

            # 將除了DATE以外的index value 字串轉為float
            pIndex = pd.IndexSlice[:, data.index.levels[1].copy().drop(DATE).tolist()]
            data.loc[pIndex, :] = data.loc[pIndex, :].astype(float)

            # DATE欄位轉為datetime
            # dIndex = pd.IndexSlice[:, [DATE]]
            # data.loc[dIndex, :] = data.loc[dIndex, :].astype('datetime64[ns, Asia/Taipei]')

            if self.data.empty:
                self.data = data
                self.data.columns = np.arange(0, data.columns.size)
            else:
                data.columns = np.arange(self.data.columns.size, self.data.columns.size + data.columns.size)
                self.data = pd.merge(self.data, data, on=['code', 'name'], how='inner')

            logging.info(f'read price for date: {dk}')

            self.dk[dk] = True

    def query(self, start, end=None):
        q = self.qDate()

        if end == None:
            r = q[start == q]
            if r.empty:
                return None
            return self.data.iloc[:, r.index[0]]

        r = q[(start <= q) & (end >= q)]

        if r.empty:
            return None

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
        self.read('202009')

        if start.__len__() == 4:
            if (end == None) | (end == ''):
                data = self.year(start)
            elif end.__len__() == 4:
                data = self.query(f"{start}-01-01", f"{end}-12-31")
            else:
                data = self.query(f"{start}-01-01", end)
        elif (end == None) | (end == ''):
            data = self.date(start)
        elif end.__len__() == 4:
            data = self.query(start, f"{end}-12-31")
        else:
            data = self.query(start, end)

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
