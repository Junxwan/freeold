# 統計弱勢股紅黑K比例

import pandas as pd
import glob
import configparser
import os
from stock import name, data

NAME = 'weak_black_red'
config = configparser.ConfigParser()
config.read('../config.ini')
data_path = os.path.abspath(dict(config['path'])['data'])
weak_path = os.path.join(data_path, 'csv', 'strategy', 'weak', 'all')
stock = data.Stock(os.path.join(data_path, 'csv', 'stock'))
stock.readAll()
dates = stock.dates()
result = []

for year in ['2020', '2019', '2018', '2017']:
    total = 0
    red = 0
    red_1_5 = 0
    black = 0

    for dir_path in sorted(glob.glob(os.path.join(weak_path, year + '*')), reverse=False):
        if os.path.isdir(dir_path) == False:
            continue

        for csv_path in sorted(glob.glob(os.path.join(dir_path, "*.csv")), reverse=False):
            date = os.path.basename(csv_path).split('.')[0]

            print(date)

            date = dates[dates.index(date) + 1]
            d = stock.date(date)

            for index, value in pd.read_csv(csv_path).iterrows():
                total += 1
                v = d[value[name.CODE]]

                if v[name.D_INCREASE] > 0:
                    red += 1
                else:
                    black += 1

                if v[name.D_INCREASE] >= 1.5:
                    red_1_5 += 1

    result.append([
        year,
        red,
        round(red / total, 2) * 100,
        red_1_5,
        round(red_1_5 / total, 2) * 100,
        black,
        round(black / total, 2) * 100,
        total
    ])

result_dir = os.path.join(data_path, 'result', NAME)

if os.path.exists(result_dir) == False:
    os.mkdir(result_dir)

pd.DataFrame(
    result,
    columns=['year', 'red', 'red%', 'red_1_5', 'red_1_5%', 'black', 'black%', 'total']
).to_csv(os.path.join(result_dir, NAME) + '.csv', index=False)
