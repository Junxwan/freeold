from . import name, data


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

    # 排序key
    sort_key = [name.CODE]

    file_columns = [
        name.CODE,
        'name',
        name.OPEN,
        name.CLOSE,
        name.HIGH,
        name.LOW,
        name.INCREASE,
        name.D_INCREASE,
        name.AMPLITUDE,
        name.VOLUME
    ]

    len = 90

    def execute(self, index, code, stock, trend, info, check_offset_day=0):
        if stock.shape[1] < self.len:
            return None

        self.stock = stock
        self.trend = trend

        if self.check_stock(self.check_stocks, i=check_offset_day) == False:
            return None

        if self.run(index, code, stock, trend, info):
            d = stock[index][1:].tolist()
            d.insert(0, code)
            d.insert(1, info['name'])
            return self.data(d, index, code, stock, trend, info)

        return None

    def data(self, data, index, code, stock, trend, info):
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
        return self.stock.loc[key].iloc[i]

    def _trend(self, key):
        return self.trend.loc[key]

    def check_stock(self, query, i=0) -> bool:
        for q in query:
            v1 = self._stock(q[0], i=i)

            if type(q[2]) == str:
                v2 = self._stock(q[2], i=i)
            else:
                v2 = q[2]

            if self.operator[q[1]](v1, v2) == False:
                return False
        return True

    def run(self, index, code, stock, trend, info) -> bool:
        return False

    def sort(self, data):
        return data.sort_values(by=self.sort_key, ascending=False)

    def limit(self, data):
        return data[:self.num]
