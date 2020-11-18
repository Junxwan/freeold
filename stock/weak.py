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

    def run(self, index, code, stock, trend, info) -> bool:
        return stock.loc[name.VOLUME][:5].mean() > 500


# 弱勢股-昨天紅
class YesterdayRed(All):
    def run(self, index, code, stock, trend, info) -> bool:
        if All.run(self, index, code, stock, trend, info):
            d = stock[index + 1]
            return d[name.OPEN] < d[name.CLOSE]
        return False

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
class YesterdayRedDIncrease1_5(YesterdayRed):
    def run(self, index, code, stock, trend, info) -> bool:
        if YesterdayRed.run(self, index, code, stock, trend, info):
            return stock[index + 1][name.D_INCREASE] >= 1.5
        return False


# 弱勢股-昨天紅-當日上漲大於等於1.5%-左頭
class YesterdayRedDIncrease1_5_LeftHead(query.Base):
    def __init__(self):
        self.query = YesterdayRedDIncrease1_5()
        self.pattern = pattern.LeftHead()
        self.query_result = None
        self.pattern_result = None

    def run(self, index, code, stock, trend, info) -> bool:
        self.query_result = self.query.execute(index, code, stock, trend, info)

        if self.query_result is None:
            return False

        self.pattern_result = self.pattern.execute(index + 1, code, stock.iloc[:, 1:], trend, info)

        if self.pattern_result is None:
            return False

        return True

    def data(self, data, index, code, stock, trend, info):
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

    def run(self, index, code, stock, trend, info) -> bool:
        self.query_result = self.query.execute(index, code, stock, trend, info)

        if self.query_result is None:
            return False

        self.pattern_result = self.pattern.execute(index + 2, code, stock.iloc[:, 2:], trend, info)

        if self.pattern_result is None:
            return False

        return True

    def data(self, data, index, code, stock, trend, info):
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

    def run(self, index, code, stock, trend, info) -> bool:
        self.query_result = self.query.execute(index, code, stock, trend, info)

        if self.query_result is None:
            return False

        self.pattern_result = self.pattern.execute(index + 2, code, stock.iloc[:, 2:], trend, info)

        if self.pattern_result is None:
            return False

        return True

    def data(self, data, index, code, stock, trend, info):
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
    'yesterday_red': YesterdayRed(),
    'yesterday_red_d_increase_1_5': YesterdayRedDIncrease1_5(),
    'yesterday_red_d_increase_1_5_left_head': YesterdayRedDIncrease1_5_LeftHead(),
    'yesterday_red_d_increase_1_5_left_head_near_right': YesterdayRedDIncrease1_5_LeftHeadNearRight(),
    'yesterday_red_d_increase_1_5_left_head_first_breakthrough': YesterdayRedDIncrease1_5_LeftHeadFirstBreakthrough(),
    'yesterday_red_d_increase_1_5_decline': YesterdayRedDIncrease1_5_Decline(),
    'yesterday_red_d_increase_1_5_platform': YesterdayRedDIncrease1_5_Platform(),
}
