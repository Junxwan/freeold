from . import name, query


# 弱勢股
class All(query.Base):
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
class YesterdayRed(All):
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
class YesterdayRedDIncrease1_5(YesterdayRed):
    def run(self, index, code, stock, trend, info) -> bool:
        if YesterdayRed.run(self, index, code, stock, trend, info):
            return stock[index + 1][name.D_INCREASE] >= 1.5
        return False

LIST = {
    'all': All(),
    'yesterday_red': YesterdayRed(),
    'yesterday_red_d_increase_1_5': YesterdayRedDIncrease1_5(),
}