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

    ys = None

    def __init__(self):
        self.pattern = data.Pattern()

    def execute(self, index, code, stock, trend, info, pattern=None, check_offset_day=0):
        self.stock = stock
        self.trend = trend
        self.pattern_model = pattern

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

    def runPattern(self, data):
        arg = self.pattern_arg()

        if self.ys is None:
            self.ys = self.pattern.ys(arg[0], arg[1], self.pattern_model)

        return self.pattern.corr_coef(data, arg[0], arg[1], self.ys, arg[2])

    def pattern_arg(self):
        return [0, 0, 0]

    def sort(self, data):
        return data.sort_values(by=self.sort_key, ascending=False)

    def limit(self, data):
        return data[:self.num]


# 弱勢股
class WeaK(Base):
    check_stocks = [
        [name.OPEN, '>', 10],
        [name.VOLUME, '>=', 1000],
        [name.AMPLITUDE, '>=', 3],
        [name.OPEN, '>', name.CLOSE],
    ]

    sort_key = [name.AMPLITUDE]

    def run(self, index, code, stock, trend, info) -> bool:
        return True


# 弱勢股-昨天紅
class WeakYesterdayRed(WeaK):
    def run(self, index, code, stock, trend, info) -> bool:
        d = stock[index + 1]
        return d[name.OPEN] < d[name.CLOSE]

    def data(self, data, index, code, stock, trend, info):
        d = stock[index + 1]
        data.append(d[name.OPEN])
        data.append(d[name.CLOSE])
        data.append(d[name.HIGH])
        data.append(d[name.LOW])
        data.append(d[name.INCREASE])
        data.append(d[name.D_INCREASE])
        data.append(d[name.AMPLITUDE])
        data.append(d[name.VOLUME])
        return data

    def columns(self):
        columns = self.file_columns.copy()
        columns.append(f'y_{name.OPEN}')
        columns.append(f'y_{name.CLOSE}')
        columns.append(f'y_{name.HIGH}')
        columns.append(f'y_{name.LOW}')
        columns.append(f'y_{name.INCREASE}')
        columns.append(f'y_{name.D_INCREASE}')
        columns.append(f'y_{name.AMPLITUDE}')
        columns.append(f'y_{name.VOLUME}')
        return columns

# 弱勢股-昨天紅-當日上漲大於等於1.5%
class WeakYesterdayRedDIncrease1_5(WeakYesterdayRed):
    def run(self, index, code, stock, trend, info) -> bool:
        if WeakYesterdayRed.run(self, index, code, stock, trend, info):
            return stock[index + 1][name.D_INCREASE] >= 1.5
        return False


# 1. 弱勢股-昨天紅
# 2. 前天之前是下降趨勢(連黑)
class WeakTodayRedBeforeBlackDown(Base):
    sort_key = [name.INCREASE]

    def __init__(self, day=None):
        Base.__init__(self)
        self.weak = WeakYesterdayRed()

        if day is None:
            self.pattern = TodayRedBeforeBlackDown()
        else:
            self.pattern = TodayRedBeforeBlackDown([day, day])

    def run(self, index, code, stock, trend, info) -> bool:
        self.weak_data = self.weak.execute(index, code, stock, trend, info, pattern=self.pattern_model)

        if self.weak_data is None:
            return False

        self.pattern_data = self.pattern.execute(
            index + 1,
            code,
            stock.iloc[:, 1:],
            trend,
            info,
            pattern=self.pattern_model
        )

        if self.pattern_data is None:
            return False

        return True

    def data(self, data, index, code, stock, trend, info):
        return self.weak_data + self.pattern_data[9:]

    def columns(self):
        columns = self.weak.columns()
        for name in self.pattern.pattern_columns:
            columns.append(name)
        return columns


# 今天紅且昨天之前是下降趨勢(連黑)
class TodayRedBeforeBlackDown(Base):
    check_stocks = [
        [name.OPEN, '<', name.CLOSE],
    ]

    sort_key = [name.INCREASE]

    pattern_columns = [name.START_DATE, name.END_DATE, name.SIMILARITY, name.LINE, name.MA]

    pattern_day = [2, 10]

    similarity = 0.85

    def __init__(self, patternDay=None):
        Base.__init__(self)

        if patternDay is not None:
            self.pattern_day = patternDay

    def run(self, index, code, stock, trend, info) -> bool:
        self.corr = self.runPattern(stock.iloc[:, 1:])

        if self.corr is None:
            return False

        d = stock.iloc[:, 1:self.corr[0] + 1]

        for i in d.columns:
            v = d[i]
            if v[name.OPEN] < v[name.CLOSE]:
                return False

        return True

    def pattern_arg(self):
        arg = self.pattern_day.copy()
        arg.append(self.similarity)
        return arg

    def data(self, data, index, code, stock, trend, info):
        d = stock.iloc[:, :self.corr[0]]
        data.append(d.iloc[0].iloc[-1])
        data.append(d.iloc[0].iloc[0])
        data.append(self.corr[1])
        data.append(self.corr[2])
        data.append(self.corr[3])
        return data

    def columns(self):
        columns = self.file_columns.copy()
        for name in self.pattern_columns:
            columns.append(name)
        return columns
