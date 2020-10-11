from . import name


class Base():
    operator = {
        '==': lambda x, y: x == y,
        '!=': lambda x, y: x != y,
        '<>': lambda x, y: x != y,
        '<': lambda x, y: x < y,
        '>': lambda x, y: x > y,
        '<=': lambda x, y: x <= y,
        '>=': lambda x, y: x >= y,
    }

    check_stocks = []

    # 最多幾筆
    num = 10000

    offset_day = 0

    # 排序key
    sort_key = []

    file_columns = ['code', 'name', name.OPEN, name.CLOSE, name.HIGH, name.LOW, name.INCREASE, name.AMPLITUDE,
                    name.VOLUME]

    def run(self, index, code, stock, trend, info):
        self.index = index
        self.code = code
        self.stock = stock
        self.trend = trend
        self.info = info

        if self.check_stock(self.check_stocks) == False:
            return None

        if self._run():
            d = self.stock[self.index][1:].tolist()
            d.insert(0, self.code)
            d.insert(1, self.info['name'])
            return self.data(d)

        return None

    def data(self, data):
        return data

    def columns(self):
        return self.file_columns

    def open(self):
        return self._stock(name.OPEN)

    def close(self):
        return self._stock(name.CLOSE)

    def high(self):
        return self._stock(name.HIGH)

    def low(self):
        return self._stock(name.LOW)

    def increase(self):
        return self._stock(name.INCREASE)

    def amplitude(self):
        return self._stock(name.AMPLITUDE)

    def volume(self):
        return self._stock(name.VOLUME)

    def trend_close(self):
        return self._trend(name.CLOSE)

    def trend_time(self):
        return self._trend(name.TIME)

    def _stock(self, key, i=0):
        d = self.stock.loc[key]
        if i > 0:
            return d.iloc[0:i]
        return d.iloc[0]

    def _trend(self, key):
        return self.trend.loc[key]

    def check_stock(self, query) -> bool:
        for q in query:
            v1 = self._stock(q[0])

            if type(q[2]) == str:
                v2 = self._stock(q[2])
            else:
                v2 = q[2]

            if self.operator[q[1]](v1, v2) == False:
                return False
        return True

    def _run(self) -> bool:
        return False

    def sort(self, data):
        return data.sort_values(by=self.sort_key, ascending=False)

    def limit(self, data):
        return data[:self.num]


class WeaK(Base):
    check_stocks = [
        [name.OPEN, '>', 10],
        [name.VOLUME, '>=', 1000],
        [name.AMPLITUDE, '>=', 3],
        [name.INCREASE, '<', 0],
        [name.OPEN, '>', name.CLOSE],
    ]

    sort_key = ['amplitude']

    def _run(self) -> bool:
        return True


class WeakRed(WeaK):
    offset_day = 1

    def _run(self) -> bool:
        d = self.stock[self.index + self.offset_day]
        return d[name.OPEN] < d[name.CLOSE]

    def data(self, data):
        d = self.stock[self.index + self.offset_day]
        data.append(d[name.INCREASE])
        data.append(d[name.AMPLITUDE])
        return data

    def columns(self):
        columns = self.file_columns.copy()
        columns.append(f'y_{name.INCREASE}')
        columns.append(f'y_{name.AMPLITUDE}')
        return columns


class OpenHighCloseLow(WeaK):
    def _run(self) -> bool:
        if self._trend is None:
            return False

        price = self.trend_close()
        q = self.trend_time()
        date = q[0][:10]
        times = [
            ['09:00:00', '09:30:00'],
            ['09:30:00', '10:00:00'],
            ['10:00:00', '10:30:00'],
        ]

        value = 10000
        for time in times:
            p = price[(q >= f'{date} {time[0]}') & (q < f'{date} {time[1]}')]

            if p.empty:
                return False

            max = float(p.max())
            if value <= max:
                return False

            value = max

        return True
