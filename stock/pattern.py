from . import name, data, query


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
class LeftHead(query.Base):
    cs = ['right_date', 'left_date', 'left_bottom_date']

    def run(self, index, code, stock, info) -> bool:
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
                left = stock[self.leftBar]

                if left.loc[name.CLOSE] > left.loc[name.OPEN]:
                    p = left.loc[name.CLOSE]
                else:
                    p = left.loc[name.OPEN]

                if p <= stock[self.rightBar].loc[name.CLOSE]:
                    continue

                i = self.leftBar - self.rightBar
                p = price.iloc[:, i:index - self.leftBar + 1 + i]

                if p.loc[name.CLOSE].min() > p.loc[name.OPEN].min():
                    self.leftBottomBar = p.loc[name.OPEN].astype(float).idxmin()
                elif self.leftBottomBar == 0:
                    self.leftBottomBar = index
                else:
                    self.leftBottomBar = p.loc[name.CLOSE].astype(float).idxmin()

                break

        if self.leftBar == 0:
            return False

        # 當前收盤價大於左頭
        if stock[self.leftBar][name.OPEN] > stock[self.leftBar][name.CLOSE]:
            if stock[self.rightBar][name.CLOSE] > stock[self.leftBar][name.OPEN]:
                return False
        else:
            if stock[self.rightBar][name.CLOSE] > stock[self.leftBar][name.CLOSE]:
                return False

        if self.leftBottomBar == 0:
            self.leftBottomBar = index

        return True

    # 左頭部漲幅
    def get_increase(self, price):
        t = data.tick(price.loc[name.HIGH].max(), price.loc[name.LOW].min())
        ts = data.ticks(price.loc[name.HIGH].max(), price.loc[name.LOW].min())

        if len(ts) < 20:
            return t * 2

        return t * 3

    def data(self, data, index, code, stock, info):
        data.append(stock[self.rightBar].loc[name.DATE])
        data.append(stock[self.leftBar].loc[name.DATE])
        data.append(stock[self.leftBottomBar].loc[name.DATE])
        return data

    def columns(self):
        columns = self.file_columns.copy()
        for c in self.cs:
            columns.append(c)
        return columns


#
# 接近左頭(0-6%)
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
    def run(self, index, code, stock, info) -> bool:
        if LeftHead.run(self, index, code, stock, info) == False:
            return False

        diff = round(stock[self.leftBar].loc[name.CLOSE] / stock[self.rightBar].loc[name.CLOSE], 2)

        if diff < 1 or diff >= 1.07:
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
    def run(self, index, code, stock, info) -> bool:
        if LeftHead.run(self, index, code, stock.iloc[:, 1:], info) == False:
            return False

        self.rightBar -= 1
        d = stock[self.leftBar]

        if d.loc[name.CLOSE] > d.loc[name.OPEN]:
            left_high = d.loc[name.CLOSE]
        else:
            left_high = d.loc[name.OPEN]

        if stock[self.rightBar].loc[name.CLOSE] <= left_high:
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
class Decline(query.Base):
    cs = ['right_date', 'left_date']

    def run(self, index, code, stock, info) -> bool:
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

    def data(self, data, index, code, stock, info):
        data.append(stock[self.rightBar].loc[name.DATE])
        data.append(stock[self.leftBar].loc[name.DATE])
        return data

    def columns(self):
        columns = self.file_columns.copy()
        for c in self.cs:
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
class Platform(query.Base):
    cs = ['right_date', 'left_date']

    def run(self, index, code, stock, info) -> bool:
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

    def data(self, data, index, code, stock, info):
        data.append(stock[self.rightBar].loc[name.DATE])
        data.append(stock[self.leftBar].loc[name.DATE])
        return data

    def columns(self):
        columns = self.file_columns.copy()
        for c in ['right_date', 'left_date']:
            columns.append(c)
        return columns


LIST = {
    'left_head': LeftHead(),
    'left_head_near_right': LeftHeadNearRight(),
    'left_head_first_breakthrough': LeftHeadFirstBreakthrough(),
    'decline': Decline(),
    'platform': Platform(),
}
