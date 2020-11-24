# 統計弱勢股昨天紅K漲幅

import math
import numpy as np
import pandas as pd
import glob
import configparser
import os
from stock import name, data

config = configparser.ConfigParser()
config.read('../config.ini')


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


def toCsv(data_path, result_path, stock=None, year=None):
    weak_path = os.path.join(data_path, 'csv', 'strategy', '', 'yesterday_red')

    if stock is None:
        stock = data.Stock(os.path.join(data_path, 'csv', 'stock'))
        stock.readAll()

    dates = stock.dates()

    if year is None:
        year = "*"
    else:
        year += "*"

    result = []
    for dir_path in sorted(glob.glob(os.path.join(weak_path, year)), reverse=False):
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


def statistics(result_path, max=None, min=0.0, lw=1.0):
    result = []
    data = pd.read_csv(result_path)
    q = data['c_increase']

    if max is None:
        max = math.ceil(q.max())

    for i in np.append(np.arange(min, max, lw), max):
        all = q[q >= i]
        ra = q[(q >= i) & (q < i + lw)]

        result.append([i, len(all), round(len(all) / len(data), 2) * 100, len(ra), round(len(ra) / len(data), 2) * 100])

    pd.DataFrame(result, columns=[
        name.INCREASE,
        f"all_{name.INCREASE}_count",
        f"all_{name.INCREASE}_count_%",
        f"{name.INCREASE}_count",
        f"{name.INCREASE}_count_%"
    ]).to_csv(os.path.join(os.path.dirname(result_path),
                           f"{os.path.basename(result_path).split('.')[0]}_statistics") + '.csv', index=False)


NAME = 'weak_red_increase'
data_path = os.path.abspath(dict(config['path'])['data'])

stock = data.Stock(os.path.join(data_path, 'csv', 'stock'))
stock.readAll()

for year in ['*', '2020', '2019', '2018', '2017']:
    result_dir = os.path.join(data_path, 'statistics', NAME)

    if os.path.exists(result_dir) == False:
        os.mkdir(result_dir)

    if year == '*':
        file_name = 'all'
    else:
        file_name = year

    result_path = os.path.join(result_dir, file_name) + '.csv'

    toCsv(data_path, result_path, stock=stock, year=year)
    statistics(result_path, max=None, min=0.0, lw=1.0)
