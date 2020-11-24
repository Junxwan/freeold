from . import name, query, pattern


# 弱勢股
class All(query.Base):
    check_stocks = [
        [name.OPEN, '>', 10],
        [name.VOLUME, '>=', 500],
        [name.AMPLITUDE, '>=', 3],
        [name.OPEN, '>', name.CLOSE],
    ]

    sort_key = [name.AMPLITUDE]

    def run(self, index, code, stock, info) -> bool:
        d = stock.loc[name.VOLUME][1:6]

        if len(d) != 5:
            raise ValueError('volume mean day is not 5')

        return d.mean() > 500


# 弱勢股-走勢圖拉高(10)走低(11)
# 1. 當日高點在10點前
# 2. 當日11點前低點與當日最高點差距有1%
class TrendHigh10Low11(All):
    sort_key = ['max_min_diff']

    def __init__(self):
        self.max = None
        self.min = None

    def run(self, index, code, stock, info) -> bool:
        if All.run(self, index, code, stock, info):
            date = stock.loc[name.DATE][0]
            trend = self.trendQ.code(code, date)

            if trend is None:
                raise ValueError(f'{code} {date} not trend')

            trend = trend.dropna(how='all', axis=1)
            trend.loc[name.PRICE] = trend.loc[name.PRICE].astype(float)

            # 當日高點在10點前
            self.max = trend[trend.loc[name.PRICE].astype(float).idxmax()]
            if self.max.loc[name.TIME] > f'{date} 10:00:00':
                return False

            # 當日11點前低點與當日最高點差距有1%
            q = trend.loc[name.TIME]
            ts = q[(q >= f'{date} 09:00:00') & (q <= f'{date} 11:00:00')]
            data = trend.loc[:, ts.index[0]:ts.index[-1]]
            self.min = trend[data.loc[:, ts.index[0]:ts.index[-1]].loc[name.PRICE].astype(float).idxmin()]

            if self.max[name.PRICE] / self.min[name.PRICE] > 1:
                return True

        return False

    def data(self, data, index, code, stock, info):
        data.append(self.max[name.TIME])
        data.append(self.max[name.PRICE])
        data.append(self.min[name.TIME])
        data.append(self.min[name.PRICE])
        data.append(round(self.max[name.PRICE] / self.min[name.PRICE], 2))
        return data

    def columns(self):
        columns = self.file_columns.copy()
        columns.append(f'max_{name.TIME}')
        columns.append(f'max_{name.PRICE}')
        columns.append(f'min_{name.TIME}')
        columns.append(f'min_{name.PRICE}')
        columns.append('max_min_diff')
        return columns


# 弱勢股-昨天紅
class YesterdayRed(All):
    def run(self, index, code, stock, info) -> bool:
        if All.run(self, index, code, stock, info):
            return self.isRed(stock)

        return False

    def isRed(self, stock):
        d = stock[stock.columns[1]]
        return d[name.OPEN] < d[name.CLOSE]

    def data(self, data, index, code, stock, info):
        return data + self.get_data(stock)

    def columns(self):
        return self.file_columns.copy() + self.get_columns()

    def get_data(self, stock):
        data = []
        d = stock[stock.columns[1]]
        data.append(d[name.OPEN])
        data.append(d[name.CLOSE])
        data.append(d[name.HIGH])
        data.append(d[name.LOW])
        data.append(d[name.INCREASE])
        data.append(d[name.D_INCREASE])
        data.append(d[name.AMPLITUDE])
        data.append(d[name.VOLUME])
        return data

    def get_columns(self):
        columns = []
        columns.append(f'y_{name.OPEN}')
        columns.append(f'y_{name.CLOSE}')
        columns.append(f'y_{name.HIGH}')
        columns.append(f'y_{name.LOW}')
        columns.append(f'y_{name.INCREASE}')
        columns.append(f'y_{name.D_INCREASE}')
        columns.append(f'y_{name.AMPLITUDE}')
        columns.append(f'y_{name.VOLUME}')
        return columns


# 弱勢股-昨天紅-走勢圖拉高(10)走低(11)
# 1. 當日高點在10點前
# 2. 當日11點前低點與當日最高點差距有1%
class YesterdayRedTrendHigh10Low11(TrendHigh10Low11):
    sort_key = ['max_min_diff']

    def __init__(self):
        TrendHigh10Low11.__init__(self)
        self.yesterday_red = YesterdayRed()

    def run(self, index, code, stock, info) -> bool:
        if TrendHigh10Low11.run(self, index, code, stock, info):
            return self.yesterday_red.isRed(stock)

        return False

    def data(self, data, index, code, stock, info):
        return TrendHigh10Low11.data(self, data, index, code, stock, info) + \
               self.yesterday_red.get_data(stock)

    def columns(self):
        return TrendHigh10Low11.columns(self) + self.yesterday_red.get_columns()


# 弱勢股-昨天紅-當日上漲大於等於1.5%
class YesterdayRedDIncrease1_5(YesterdayRed):
    def run(self, index, code, stock, info) -> bool:
        if YesterdayRed.run(self, index, code, stock, info):
            return stock[stock.columns[1]][name.D_INCREASE] >= 1.5
        return False


# 弱勢股-昨天紅-當日上漲大於等於1.5%-左頭
class YesterdayRedDIncrease1_5_LeftHead(query.Base):
    def __init__(self):
        self.query = YesterdayRedDIncrease1_5()
        self.pattern = pattern.LeftHead()
        self.query_result = None
        self.pattern_result = None

    def run(self, index, code, stock, info) -> bool:
        self.query_result = self.query.execute(index, code, stock, info)

        if self.query_result is None:
            return False

        self.pattern_result = self.pattern.execute(index + 1, code, stock.iloc[:, 1:], info)

        if self.pattern_result is None:
            return False

        return True

    def data(self, data, index, code, stock, info):
        for v in self.pattern_result[-3:]:
            self.query_result.append(v)

        return self.query_result

    def columns(self):
        columns = self.query.columns().copy()
        for v in self.pattern.cs:
            columns.append(v)

        return columns


# 弱勢股-昨天紅-當日上漲大於等於1.5%-接近左頭
class YesterdayRedDIncrease1_5_LeftHeadNearRight(YesterdayRedDIncrease1_5_LeftHead):
    def __init__(self):
        YesterdayRedDIncrease1_5_LeftHead.__init__(self)
        self.pattern = pattern.LeftHeadNearRight()


# 弱勢股-昨天紅-當日上漲大於等於1.5%-第一次突破左頭
class YesterdayRedDIncrease1_5_LeftHeadFirstBreakthrough(YesterdayRedDIncrease1_5_LeftHead):
    def __init__(self):
        YesterdayRedDIncrease1_5_LeftHead.__init__(self)
        self.pattern = pattern.LeftHeadFirstBreakthrough()


# 弱勢股-昨天紅-當日上漲大於等於1.5%-下降
class YesterdayRedDIncrease1_5_Decline(query.Base):
    def __init__(self):
        self.query = YesterdayRedDIncrease1_5()
        self.pattern = pattern.Decline()
        self.query_result = None
        self.pattern_result = None

    def run(self, index, code, stock, info) -> bool:
        self.query_result = self.query.execute(index, code, stock, info)

        if self.query_result is None:
            return False

        self.pattern_result = self.pattern.execute(index + 2, code, stock.iloc[:, 2:], info)

        if self.pattern_result is None:
            return False

        return True

    def data(self, data, index, code, stock, info):
        for v in self.pattern_result[-2:]:
            self.query_result.append(v)

        return self.query_result

    def columns(self):
        columns = self.query.columns().copy()
        for v in self.pattern.cs:
            columns.append(v)

        return columns


# 弱勢股-昨天紅-當日上漲大於等於1.5%-盤整
class YesterdayRedDIncrease1_5_Platform(query.Base):
    def __init__(self):
        self.query = YesterdayRedDIncrease1_5()
        self.pattern = pattern.Platform()
        self.query_result = None
        self.pattern_result = None

    def run(self, index, code, stock, info) -> bool:
        self.query_result = self.query.execute(index, code, stock, info)

        if self.query_result is None:
            return False

        self.pattern_result = self.pattern.execute(index + 2, code, stock.iloc[:, 2:], info)

        if self.pattern_result is None:
            return False

        return True

    def data(self, data, index, code, stock, info):
        for v in self.pattern_result[-2:]:
            self.query_result.append(v)

        return self.query_result

    def columns(self):
        columns = self.query.columns().copy()
        for v in self.pattern.cs:
            columns.append(v)

        return columns


LIST = {
    'all': All(),
    'trend_high10_low11': TrendHigh10Low11(),
    'yesterday_red': YesterdayRed(),
    'yesterday_red_trend_high10_low11': YesterdayRedTrendHigh10Low11(),
    'yesterday_red_d_increase_1_5': YesterdayRedDIncrease1_5(),
    'yesterday_red_d_increase_1_5_left_head': YesterdayRedDIncrease1_5_LeftHead(),
    'yesterday_red_d_increase_1_5_left_head_near_right': YesterdayRedDIncrease1_5_LeftHeadNearRight(),
    'yesterday_red_d_increase_1_5_left_head_first_breakthrough': YesterdayRedDIncrease1_5_LeftHeadFirstBreakthrough(),
    'yesterday_red_d_increase_1_5_decline': YesterdayRedDIncrease1_5_Decline(),
    'yesterday_red_d_increase_1_5_platform': YesterdayRedDIncrease1_5_Platform(),
}
