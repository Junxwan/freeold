import copy
import json
import os
import glob
import pandas as pd
import numpy as np

# 開盤價
from datetime import datetime

DATE = 'date'

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

# 個股行情資料
DATA_DIR = {
    'price': [OPEN, CLOSE, HIGH, LOW, INCREASE, AMPLITUDE],
    'volume': [VOLUME],
}

COLUMNS = [OPEN, CLOSE, HIGH, LOW, INCREASE, AMPLITUDE, VOLUME]

# 個股基本資料
INFO_FILE_NAME = 'stock.json'


# 個股行情資料
class stock:
    _data = {}
    _item = {}
    _dirs = {}
    _dir = ''

    def __init__(self, dir):
        self._dir = dir

        for name, dirs in DATA_DIR.items():
            for d in dirs:
                self._dirs[d] = os.path.join(dir, name, d)
                self._item[d] = []

    # 某天資料
    def day(self, date):
        data = self._data.get(date)

        if data == None:
            self._data[date] = {}
            m = f'{date[:4]}{date[5:7]}'

            for dir, path in self._dirs.items():
                pd.read_json(os.path.join(path, m, f'{date}.json'), encoding='utf-8')

                file = open(os.path.join(path, m, f'{date}.json'), encoding='utf-8')
                data = json.load(file)

                if data['date'] == date:
                    self._data[date][dir] = data['value']

        return self._data[date]

    # 某月資料
    def month(self, month):
        dates = []
        path = os.path.join(self._dirs[OPEN], month)

        for f in os.listdir(path):
            n = os.path.splitext(f)
            if n[-1] == '.json':
                self.day(n[0])
                dates.append(n[0])

        return [{k: self._data[k]} for k in dates][0]

    def codes(self, date):
        return [{'code': k, 'name': v['name']} for k, v in self.day(date)[OPEN].items()]

    # 某個股某天數範圍資料
    def code(self, code, date=None, keyName=False, keys=None):
        data = copy.deepcopy(self._item)

        if type(date) != list:
            date = [date]

        for d in date:
            for name, value in self.day(d).items():
                data[name].append(value[code]['value'])

        if keys != None:
            ks = set([k for k in self._item]) - set(keys)

            for k in ks:
                del data[k]

        if keyName == True:
            return [data[k] for k in data.keys()]

        return data

    # 開市日
    def dates(self, year, month=None):
        dates = []
        path = os.path.join(self._dir, f'price/{OPEN}')

        for d in sorted(os.listdir(path), reverse=True):
            fullPath = os.path.join(path, d)

            if os.path.isdir(fullPath):
                for f in sorted(os.listdir(fullPath), reverse=True):
                    n = os.path.splitext(f)

                    if n[-1] != '.json':
                        continue

                    if n[0][:4] != year:
                        continue

                    if (month != None) & (n[0][5:7] != month):
                        continue

                    dates.append(n[0])
        return dates

    def afterDates(self, date):
        dates = []

        for ym in diffMonth(date):
            for t in self.dates(ym[:4], ym[4:]):
                if int(date.replace('-', '')) >= int(t.replace('-', '')):
                    break

                dates.append(t)

        return dates


class stocks():
    data = pd.DataFrame()
    m = {}

    def __init__(self, dir):
        self.dir = dir

    def year(self, year):
        for path in sorted(glob.glob(os.path.join(self.dir, f'{year}*.csv')), reverse=True):
            self.read(os.path.basename(path).split('.')[0])

    def month(self, m):
        self.read(m)
        q = self.queryDate()
        r = q[(f"{m[:4]}-{m[4:6]}-01" <= q) & (f"{m[:4]}-{m[4:6]}-31" >= q)].index

        self.data[r[0]:r[-1]]
        self.data.loc['33']
        pass

    def date(self, date):
        self.read(self.getM(date))
        q = self.queryDate()
        return self.data[q[q == date].index[0]]

    def read(self, m):
        if m not in self.m:
            data = pd.read_csv(os.path.join(self.dir, f'{m}.csv'), index_col=[0, 1], header=[0])

            if self.data.empty:
                self.data = data
            else:
                data.columns = np.arange(self.data.columns.size, self.data.columns.size + data.columns.size)
                self.data = pd.merge(self.data, data, on=['code', 'name'], how='inner')

    def queryDate(self):
        return self.data.loc[2330].loc['date']

    def getM(self, date):
        return f'{date[:4]}{date[5:7]}'


def diffMonth(date):
    nowDate = datetime.now()
    date = datetime.fromisoformat(date)

    l = []
    for year in range(date.year, nowDate.year + 1):
        max = 13
        min = 1

        if year == nowDate.year:
            max = nowDate.month + 1

            if date.year == nowDate.year:
                min = date.month
            else:
                min = 1

        elif year == date.year:
            min = date.month
            max = 13

        for m in range(min, max):
            l.append(f"{year}{m:02}")

    return sorted(l, reverse=True)
