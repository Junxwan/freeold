# 統計弱勢股昨天紅K漲幅

import pandas as pd
import glob
import configparser
import os
from stock import name, data

config = configparser.ConfigParser()
config.read('../config.ini')
data_path = os.path.abspath(dict(config['path'])['data'])
result_path = os.path.join(data_path, 'weak_increase') + '.csv'


def tick(price):
    level = [
        [10, 0.01],
        [50, 0.05],
        [100, 0.1],
        [500, 0.5],
        [1000, 1],
        [10000, 5]
    ]

    for v in level:
        if price < v[0]:
            return v

    return level[0]


def toCsv():
    weak_path = os.path.join(data_path, 'csv', 'strategy', 'weak', 'yesterday_red')
    stock = data.Stock(os.path.join(data_path, 'csv', 'stock'))
    stock.readAll()
    dates = stock.dates()

    result = []
    for dir_path in sorted(glob.glob(os.path.join(weak_path, "*")), reverse=False):
        if os.path.isdir(dir_path) == False:
            continue

        for csv_path in sorted(glob.glob(os.path.join(dir_path, "*.csv")), reverse=False):
            date = os.path.basename(csv_path).split('.')[0]

            print(date)
            date = dates[dates.index(date) + 1]

            for index, value in pd.read_csv(csv_path).iterrows():
                increase = value[f"y_{name.INCREASE}"]

                if increase >= 10.5:
                    continue

                open = value[f"y_{name.OPEN}"]
                close = value[f"y_{name.CLOSE}"]
                code = value[name.CODE]

                [otp, ot] = tick(open)
                [ctp, ct] = tick(close)

                if ot == ct:
                    t = round((close - open) / ot)
                else:
                    t = round((otp - open) / ot) + round((close - otp) / ct)

                result.append([
                    code,
                    date,
                    increase,
                    value[f"y_{name.AMPLITUDE}"],
                    t,
                    round(((close - open) / open) * 100, 2),
                    open,
                    close,
                    value[f"y_{name.HIGH}"],
                    value[f"y_{name.LOW}"],
                    value[f"y_{name.VOLUME}"]
                ])

    pd.DataFrame(
        result,
        columns=[
            name.CODE, name.DATE, name.INCREASE, name.AMPLITUDE, 'tick', f"c_{name.INCREASE}", name.OPEN,
            name.CLOSE, name.HIGH, name.LOW, name.VOLUME
        ]
    ).to_csv(result_path)


def statistics():
    result = []
    data = pd.read_csv(result_path)
    q = data['c_increase']

    all = q[q >= 10]
    ra = q[(q >= 10) & (q < 10 + 1)]

    result.append([10, len(all), round(len(all) / len(data), 2) * 100, len(ra), round(len(ra) / len(data), 2) * 100])

    for i in reversed(range(10)):
        all = q[q >= i]
        ra = q[(q >= i) & (q < i + 1)]

        result.append([i, len(all), round(len(all) / len(data), 2) * 100, len(ra), round(len(ra) / len(data), 2) * 100])

    pd.DataFrame(result, columns=[
        name.INCREASE,
        f"all_{name.INCREASE}_count",
        f"all_{name.INCREASE}_count_%",
        f"{name.INCREASE}_count",
        f"{name.INCREASE}_count_%"
    ]).to_csv(os.path.join(data_path, 'weak_increase_statistics') + '.csv', index=False)


toCsv()
statistics()
