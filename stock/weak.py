from . import name, query, pattern


# 弱勢股
class All(query.Base):
    check_stocks = [
        [name.VOLUME, '>=', 500],
        [name.AMPLITUDE, '>=', 3],
        [name.OPEN, '>', name.CLOSE],
    ]

    sort_key = [name.D_INCREASE]

    def run(self, index, code, stock, info) -> bool:
        date = stock.loc[name.DATE].iloc[0]
        trend = self.trendQ.code(code, date)

        if trend is not None and trend.dropna(how='all', axis=1).shape[1] <= 54:
            return False

        return True


# 弱勢股-走勢圖拉高(0930)走低(11)
# 1. 當日高點在0930點前
# 2. 當日11點前低點與當日最高點差距有2%
class TrendHigh0930Low11(All):
    sort_key = [name.D_INCREASE]

    def __init__(self):
        self.max = None
        self.min = None

    def run(self, index, code, stock, info) -> bool:
        if All.run(self, index, code, stock, info):
            date = stock.loc[name.DATE].iloc[0]
            trend = self.trendQ.code(code, date)

            if trend is None:
                raise ValueError(f'{code} {date} not trend')

            trend = trend.dropna(how='all', axis=1)
            trend.loc[name.PRICE] = trend.loc[name.PRICE].astype(float)

            if trend.loc[name.PRICE].dropna().empty:
                return False

            # 當日高點在0930點前
            self.max = trend[trend.loc[name.PRICE].astype(float).idxmax()]
            if self.max.loc[name.TIME] > f'{date} 09:30:00':
                return False

            # 當日11點前低點與當日最高點差距有2%
            q = trend.loc[name.TIME]
            ts = q[(q >= f'{date} 09:00:00') & (q <= f'{date} 11:00:00')]
            data = trend.loc[:, ts.index[0]:ts.index[-1]]
            self.min = trend[data.loc[:, ts.index[0]:ts.index[-1]].loc[name.PRICE].astype(float).idxmin()]

            if (self.max[name.PRICE] / self.min[name.PRICE] > 1.02) and (self.max[name.TIME] < self.min[name.TIME]):
                return True

        return False

    def data(self, data, index, code, stock, info):
        data.append(self.max[name.TIME])
        data.append(self.max[name.PRICE])
        data.append(self.min[name.TIME])
        data.append(self.min[name.PRICE])
        data.append(round(((self.max[name.PRICE] / self.min[name.PRICE]) - 1) * 100, 2))
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
        # 不准因事件性因素而出現跨日
        if stock.columns[1] - stock.columns[0] > 1:
            return False

        d = stock[stock.columns[1]]
        return d[name.OPEN] < d[name.CLOSE]

    def data(self, data, index, code, stock, info):
        return data + self.get_data(stock)

    def columns(self):
        return self.file_columns.copy() + self.get_columns()

    def get_data(self, stock):
        data = []
        volume = stock.loc[name.VOLUME]
        d1 = stock[stock.columns[1]]

        if volume.iloc[2] > 0:
            vb1 = round(d1[name.VOLUME] / volume.iloc[2], 2)
        else:
            vb1 = d1[name.VOLUME]

        vma5_1 = round(volume[1:6].sum() / 5)
        vma10_1 = round(volume[1:11].sum() / 10)
        vma20_1 = round(volume[1:21].sum() / 20)
        vma60_1 = round(volume[1:61].sum() / 60)

        data.append(d1[name.OPEN])
        data.append(d1[name.CLOSE])
        data.append(d1[name.HIGH])
        data.append(d1[name.LOW])
        data.append(d1[name.INCREASE])
        data.append(d1[name.D_INCREASE])
        data.append(d1[name.AMPLITUDE])
        data.append(d1[name.VOLUME])
        data.append(volume.iloc[2])
        data.append(round(volume.iloc[0] / d1[name.VOLUME], 2))
        data.append(vb1)
        data.append(vma5_1)
        data.append(vma10_1)
        data.append(vma20_1)
        data.append(vma60_1)
        data.append(round(d1[name.VOLUME] / vma5_1, 2))
        data.append(round(d1[name.VOLUME] / vma10_1, 2))
        data.append(round(d1[name.VOLUME] / vma20_1, 2))
        data.append(round(d1[name.VOLUME] / vma60_1, 2))
        return data

    def get_columns(self):
        columns = []
        columns.append(f'{name.OPEN}[1]')
        columns.append(f'{name.CLOSE}[1]')
        columns.append(f'{name.HIGH}[1]')
        columns.append(f'{name.LOW}[1]')
        columns.append(f'{name.INCREASE}[1]')
        columns.append(f'{name.D_INCREASE}[1]')
        columns.append(f'{name.AMPLITUDE}[1]')
        columns.append(f'{name.VOLUME}[1]')
        columns.append(f'{name.VOLUME}[2]')
        columns.append('y_volume%')
        columns.append('y_volume[1]%')
        columns.append('5vma[1]')
        columns.append('10vma[1]')
        columns.append('20vma[1]')
        columns.append('60vma[1]')
        columns.append('5vma[1]%')
        columns.append('10vma[1]%')
        columns.append('20vma[1]%')
        columns.append('60vma[1]%')
        return columns


# 弱勢股-昨天紅-走勢圖拉高(10)走低(11)
# 1. 當日高點在10點前
# 2. 當日11點前低點與當日最高點差距有2%
class YesterdayRedTrendHigh0930Low11(TrendHigh0930Low11):
    sort_key = ['max_min_diff']

    def __init__(self):
        TrendHigh0930Low11.__init__(self)
        self.yesterday_red = YesterdayRed()

    def run(self, index, code, stock, info) -> bool:
        if TrendHigh0930Low11.run(self, index, code, stock, info):
            return self.yesterday_red.isRed(stock)

        return False

    def data(self, data, index, code, stock, info):
        return TrendHigh0930Low11.data(self, data, index, code, stock, info) + \
               self.yesterday_red.get_data(stock)

    def columns(self):
        return TrendHigh0930Low11.columns(self) + self.yesterday_red.get_columns()


# 弱勢股-昨天紅-左頭-走勢圖拉高(10)走低(11)
# 1. 當日高點在10點前
# 2. 當日11點前低點與當日最高點差距有2%
class YesterdayRedTrendHigh0930Low11_LeftHead(YesterdayRedTrendHigh0930Low11):
    def __init__(self):
        YesterdayRedTrendHigh0930Low11.__init__(self)
        self.pattern = pattern.LeftHead()
        self.pattern_result = None

    def run(self, index, code, stock, info) -> bool:
        if YesterdayRedTrendHigh0930Low11.run(self, index, code, stock, info) == False:
            return False

        self.pattern_result = self.pattern.execute(stock.columns[1], code, stock.iloc[:, 1:], info)

        if self.pattern_result is None:
            return False

        return True

    def data(self, data, index, code, stock, info):
        data = YesterdayRedTrendHigh0930Low11.data(self, data, index, code, stock, info)
        for v in self.pattern_result[-3:]:
            data.append(v)

        return data

    def columns(self):
        columns = YesterdayRedTrendHigh0930Low11.columns(self).copy()
        for v in self.pattern.cs:
            columns.append(v)

        return columns


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
    'trend_high0930_low11': TrendHigh0930Low11(),
    'yesterday_red': YesterdayRed(),
    'yesterday_red_trend_high0930_low11': YesterdayRedTrendHigh0930Low11(),
    'yesterday_red_trend_high0930_low11_left_head': YesterdayRedTrendHigh0930Low11_LeftHead(),

    'yesterday_red_d_increase_1_5_left_head': YesterdayRedDIncrease1_5_LeftHead(),
    'yesterday_red_d_increase_1_5_left_head_near_right': YesterdayRedDIncrease1_5_LeftHeadNearRight(),
    'yesterday_red_d_increase_1_5_left_head_first_breakthrough': YesterdayRedDIncrease1_5_LeftHeadFirstBreakthrough(),
    'yesterday_red_d_increase_1_5_decline': YesterdayRedDIncrease1_5_Decline(),
    'yesterday_red_d_increase_1_5_platform': YesterdayRedDIncrease1_5_Platform(),
}
