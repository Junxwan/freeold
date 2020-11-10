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


# 左頭
#
#     * * * * * (2)
#    *         *                                    * (1)
#   *           *                                 *
#  *             *                              *
# * (3)           *                           *
#                  *                        *
#                   *                     *
#                     *                 *
#                       * * * * * * * *
#
# 1. 如果(2)高點(黑k的開盤價,紅k的收盤價)必須大於(1)收盤價
# 2. (1)必須先創低(小於黑k的收盤價,紅k的開盤價)
# 3. 創低需達到某幅度
# 4. 創低後開始反彈且達到某幅度為(2)，持續創高則更新(2)
# 5. (2)開始不繼續創高差距達幾根K棒後確認為(3)，也就是(2)必須是高點大於(3)跟(1)
# 6. (3)必須是(2)與(3)之間的最低點(黑k的收盤價,紅k的開盤價)
#
class LeftHead(Base):
    def run(self, index, code, stock, trend, info) -> bool:
        price = stock.iloc[:, :90]

        _high = 0
        _low = price.iloc[:, 0].loc[name.CLOSE]
        increase = self.get_increase(price)
        flag = 0
        self.rightBar = price.columns[0]
        self.leftBar = 0
        self.leftBottomBar = 0

        for index, value in price.items():
            close = value[name.CLOSE]
            open = value[name.OPEN]

            if close > open:
                high = close
            else:
                high = open

            # 創新低
            if _low > close:
                _low = close
                flag = 1

            # 創新低之後開始反彈達某漲幅
            if flag == 1 and (high - _low) >= increase:
                flag = 2
                _high = high
                self.leftBar = index

            # 開始反彈又創高
            if flag == 2 and high > _high:
                _high = high
                self.leftBar = index

            # 反彈後又回檔達某漲幅
            if (_high - high) >= increase and index - self.leftBar > 3:
                self.leftBottomBar = index
                break

        if self.leftBar == 0 | self.leftBottomBar == 0:
            return False

        if stock[self.leftBar].loc[name.CLOSE] <= stock[self.rightBar].loc[name.CLOSE]:
            return False

        return True

    # 左頭部漲幅
    def get_increase(self, price):
        t = data.tick(price.loc[name.HIGH].max(), price.loc[name.LOW].min())
        ts = data.ticks(price.loc[name.HIGH].max(), price.loc[name.LOW].min())

        if len(ts) < 20:
            return t * 2

        return t * 3

    def data(self, data, index, code, stock, trend, info):
        data.append(stock[self.rightBar].loc[name.DATE])
        data.append(stock[self.leftBar].loc[name.DATE])
        data.append(stock[self.leftBottomBar].loc[name.DATE])
        return data

    def columns(self):
        columns = self.file_columns.copy()
        for c in ['right_date', 'left_date', 'left_bottom_date']:
            columns.append(c)
        return columns


#
# 接近左頭
#
#     * * * * * (2)
#    *         *                                    * (1)
#   *           *                                 *
#  *             *                              *
# * (3)           *                           *
#                  *                        *
#                   *                     *
#                     *                 *
#                       * * * * * * * *
#
class LeftHeadNearRight(LeftHead):
    def run(self, index, code, stock, trend, info) -> bool:
        if LeftHead.run(self, index, code, stock, trend, info) == False:
            return False

        if round(stock[self.rightBar].loc[name.CLOSE] * 1.06, 2) < stock[self.leftBar].loc[name.CLOSE]:
            return False

        return True


#
# 股價今日突破左頭
#
#                                                       * (1)
#     * * * * * (2)                                   *
#    *         *                                    *
#   *           *                                 *
#  *             *                              *
# * (3)           *                           *
#                  *                        *
#                   *                     *
#                     *                 *
#                       * * * * * * * *
#
class LeftHeadFirstBreakthrough(LeftHead):
    def run(self, index, code, stock, trend, info) -> bool:
        if LeftHead.run(self, index, code, stock.iloc[:, 1:], trend, info) == False:
            return False

        self.rightBar -= 1

        if stock[self.rightBar].loc[name.CLOSE] < stock[self.leftBar].loc[name.CLOSE]:
            return False

        return True


# 下降
#
#
#  * * * * * (3)
#            *
#              *
#                *
#                  * * * * * (2)
#                           *
#                            *
#                             *
#                              * * * * * * * * (1)
#
# 1. 當前高點(黑k的開盤價,紅k的收盤價)必須大於前五期高點(黑k的開盤價,紅k的收盤價)
# 2. 當前高點跟前五期高點必須達到某幅度
# 3. 如果上述不成立則前五期改為前十期
#
class Decline(Base):
    def run(self, index, code, stock, trend, info) -> bool:
        price = stock.iloc[:, :90]

        self.rightBar = price.columns[0]
        self.leftBar = 0
        t = data.tick(price.loc[name.HIGH].max(), price.loc[name.LOW].min())
        increase = (t / 2)

        for index, value in price.items():
            close = value[name.CLOSE]
            open = value[name.OPEN]

            if close > open:
                high = close
            else:
                high = open

            i = index + 5
            v = price[i]
            v_close = v[name.CLOSE]
            v_open = v[name.OPEN]

            if v_close > v_open:
                v_high = v_close
            else:
                v_high = v_open

            if v_high <= high and round(v_high - high, 2) < increase:
                i = index + 10
                v = price[i]
                v_close = v[name.CLOSE]
                v_open = v[name.OPEN]

                if v_close > v_open:
                    v_high = v_close
                else:
                    v_high = v_open

                if round(v_high - high, 2) < increase * 0.7:
                    break

            self.leftBar = i

        if self.leftBar == 0:
            return False

        d = price.iloc[:, :self.leftBar - self.rightBar + 1]

        if d.loc[name.CLOSE].max() > d.loc[name.OPEN].max():
            self.leftBar = d.loc[name.CLOSE].astype(float).idxmax()
        else:
            self.leftBar = d.loc[name.OPEN].astype(float).idxmax()

        return True

    def data(self, data, index, code, stock, trend, info):
        data.append(stock[self.rightBar].loc[name.DATE])
        data.append(stock[self.leftBar].loc[name.DATE])
        return data

    def columns(self):
        columns = self.file_columns.copy()
        for c in ['right_date', 'left_date']:
            columns.append(c)
        return columns


# 盤整
#
# * * * * * * * * * * * * *
# *                       *
# *                       *
# *                       *
# * * * * * * * * * * * * *
#
#
class Platform(Base):
    def run(self, index, code, stock, trend, info) -> bool:
        price = stock.iloc[:, :90]

        self.rightBar = price.columns[0]
        self.leftBar = 0
        _highs = []
        _lows = []
        l = 5

        ts = data.ticks(price.loc[name.HIGH].max(), price.loc[name.LOW].min())
        t = data.tick(price.loc[name.HIGH].max(), price.loc[name.LOW].min())
        if len(ts) < 20:
            increase = t * 2
        else:
            increase = t * 3

        for index, value in price.items():
            close = value[name.CLOSE]
            open = value[name.OPEN]

            if close > open:
                _highs.insert(0, close)
                _lows.insert(0, open)
            else:
                _highs.insert(0, open)
                _lows.insert(0, close)

            if len(_highs) > l:
                if max(_highs) - min(_highs) > increase:
                    break

                if max(_lows) - min(_lows) > increase:
                    break

                self.leftBar = index

        if self.leftBar == 0:
            return False

        return True

    def data(self, data, index, code, stock, trend, info):
        data.append(stock[self.rightBar].loc[name.DATE])
        data.append(stock[self.leftBar].loc[name.DATE])
        return data

    def columns(self):
        columns = self.file_columns.copy()
        for c in ['right_date', 'left_date']:
            columns.append(c)
        return columns
