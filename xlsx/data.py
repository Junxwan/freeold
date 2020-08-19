import copy
import json
import os

# 開盤價
OPEN = 'open'

# 收盤價
CLOSE = 'close'

# 最高價
MAX = 'max'

# 最低價
MIN = 'min'

# 漲幅
INCREASE = 'increase'

# 震幅
AMPLITUDE = 'amplitude'

# 成交量
VOLUME = 'volume'

# 個股行情資料
DATA_DIR = {
    'price': [OPEN, CLOSE, MAX, MIN, INCREASE, AMPLITUDE],
    'volume': [VOLUME],
}

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
                file = open(os.path.join(path, m, f'{date}.json'))
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

    for d in os.listdir(path):
        fullPath = os.path.join(path, d)

        if os.path.isdir(fullPath):
            for f in os.listdir(fullPath):
                n = os.path.splitext(f)

                if n[-1] != '.json':
                    continue

                if n[0][:4] != year:
                    continue

                if (month != None) & (n[0][5:7] != month):
                    continue

                dates.append(n[0])
    return dates
