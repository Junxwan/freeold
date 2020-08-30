import copy
import json
import os
import glob
import pandas as pd
import numpy as np

# 開盤價
from datetime import datetime

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
    data = {}
    dirs = {}

    def __init__(self, dir):
        self.dir = dir

        for name, dirs in DATA_DIR.items():
            for d in dirs:
                self.dirs[d] = os.path.join(dir, name, d)

    def date(self, date):
        for dir, path in self.dirs.items():
            p = pd.read_json(os.path.join(path, self._m(date), f'{date}.json'), encoding='utf-8')

    def month(self, m):
        dates = [
            os.path.basename(k).split('.')[0]
            for k in glob.glob(os.path.join(list(self.dirs.values())[0], m, '*.json'))
        ]

        dates.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'), reverse=True)

        for date in dates:
            d = {}
            for dir, path in self.dirs.items():
                for i, v in pd.read_json(os.path.join(path, m, f'{date}.json')).iterrows():
                    code = v['code']

                    if code not in d:
                        d[code] = [date]

                    d[code].append(v['value'])

            for c, v in d.items():
                if c not in self.data:
                    self.data[c] = pd.DataFrame(v, columns=COLUMNS)

                else:
                    self.data[c].append(pd.DataFrame(v, columns=COLUMNS))

                pass


def _m(self, date):
    return f'{date[:4]}{date[5:7]}'


# 開市日
def dates(self, year, month=None):
    dates = []
    path = os.path.join(self.dir, f'price/{OPEN}')

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

    return pd.DataFrame(data=dates, columns={'date'})


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
