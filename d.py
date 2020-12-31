import math
import pyautogui
import time
import pandas as pd
import numpy as np
import os
import glob
from stock import data, name
import matplotlib.pyplot as plt

data.calendar_xy('2020-01-03')
data.calendar_xy('2020-02-03')
data.calendar_xy('2020-03-03')

stock = data.Stock('D:\\data\\csv\\stock')

# data.calendar_xy('2019-01-02')  # 23 4 1
# data.calendar_xy('2020-01-02')  # 11 5 1
# data.calendar_xy('2019-01-02', year=2020, month=8)  # 19 4 1
# data.calendar_xy('2018-09-21', year=2020, month=8)  # 23 6 4

d = {}
d1 = []


def DirToCode(path):
    for p in glob.glob(f"{path}\\*\\*.csv"):
        for i, v in pd.read_csv(p).iterrows():
            d1.append([v['code'], v['name'], os.path.basename(p).split('.')[0]])

    pd.DataFrame(d1, columns=['code', 'name', 'date']).to_csv(os.path.join(path, 'code.csv'), encoding='utf-8-sig',
                                                              index=False)


def ToDirCsv(path):
    for i, v in pd.read_csv(path).iterrows():
        code = v['name'].split('(')[1].split('.')[0]
        n = v['name'].split('(')[0]

        if str(code)[-1] == 'L' or str(code)[-1] == 'R' or str(code)[-1] == 'B' or str(code)[-1] == 'U' or int(
                code) <= 999:
            continue

        if int(code) >= 6200 and int(code) <= 6299:
            continue

        if v['date'] not in d:
            d[v['date']] = []

        d[v['date']].append([
            code,
            n,
            v['date'],
        ])

        d1.append([
            code,
            n,
            v['date'],
        ])

    for k, v in d.items():
        pd.DataFrame(v, columns=[name.CODE, name.NAME, name.DATE]).to_csv(
            os.path.join(os.path.dirname(path), 'all', f"{k}.csv"),
            encoding='utf-8-sig',
            index=False
        )

    pd.DataFrame(d1, columns=[name.CODE, name.NAME, name.DATE]).to_csv(
        os.path.join(os.path.dirname(path), 'code.csv'),
        encoding='utf-8-sig',
        index=False
    )


def ToData(path):
    columns = [
        name.CODE,
        name.NAME,
        name.DATE,
        'm',

        name.OPEN,
        name.CLOSE,
        name.HIGH,
        name.LOW,
        name.VOLUME,
        name.INCREASE,
        name.D_INCREASE,
        name.AMPLITUDE,

        f"y{name.OPEN}",
        f"y{name.CLOSE}",
        f"y{name.HIGH}",
        f"y{name.LOW}",
        f"y{name.VOLUME}",
        f"y{name.INCREASE}",
        f"y{name.D_INCREASE}",
        f"y{name.AMPLITUDE}",
        f"y{name.MAX}",

        f"yy{name.OPEN}",
        f"yy{name.CLOSE}",
        f"yy{name.HIGH}",
        f"yy{name.LOW}",
        f"yy{name.VOLUME}",
        f"yy{name.INCREASE}",
        f"yy{name.D_INCREASE}",
        f"yy{name.AMPLITUDE}",

        f"y{name.OPEN}3",
        f"y{name.CLOSE}3",
        f"y{name.HIGH}3",
        f"y{name.LOW}3",
        f"y{name.VOLUME}3",
        f"y{name.INCREASE}3",
        f"y{name.D_INCREASE}3",
        f"y{name.AMPLITUDE}3",

        f"y{name.OPEN}4",
        f"y{name.CLOSE}4",
        f"y{name.HIGH}4",
        f"y{name.LOW}4",
        f"y{name.VOLUME}4",
        f"y{name.INCREASE}4",
        f"y{name.D_INCREASE}4",
        f"y{name.AMPLITUDE}4",

        'y5ma',
        'y10ma',
        'y20ma',
        'yy5ma',
        'yy10ma',
        'yy20ma',
        'y60h',
        'ybbup',
        'ybbdo',
        'ybbw',
        'yybbw',
        'y510ma%',
        'y1020ma%',
        'y51020ma%',
        'y520ma%',
        'yv%',
        'y5v%',
        'y10v%',
        'y20v%',
    ]

    stock.readAll()

    for i, v in pd.read_csv(path).iterrows():
        if str(v[name.CODE])[-1] == 'L':
            continue

        try:
            value = stock.date(v[name.DATE]).loc[int(v[name.CODE])]
            yesterday = stock.yesterday(int(v[name.CODE]), v[name.DATE])
            yyesterday = stock.yesterday(int(v[name.CODE]), yesterday[name.DATE])
            values = stock.query(v[name.DATE], end=False).loc[int(v[name.CODE])].dropna(axis=1)

            yesterday3 = stock.yesterday(int(v[name.CODE]), yyesterday[name.DATE])
            yesterday4 = None

            if yesterday3 is None:
                yesterday3 = {}
                yesterday3[name.OPEN] = 0
                yesterday3[name.CLOSE] = 0
                yesterday3[name.HIGH] = 0
                yesterday3[name.LOW] = 0
                yesterday3[name.VOLUME] = 0
                yesterday3[name.INCREASE] = 0
                yesterday3[name.D_INCREASE] = 0
                yesterday3[name.AMPLITUDE] = 0
            else:
                yesterday4 = stock.yesterday(int(v[name.CODE]), yesterday3[name.DATE])

            if yesterday4 is None:
                yesterday4 = {}
                yesterday4[name.OPEN] = 0
                yesterday4[name.CLOSE] = 0
                yesterday4[name.HIGH] = 0
                yesterday4[name.LOW] = 0
                yesterday4[name.VOLUME] = 0
                yesterday4[name.INCREASE] = 0
                yesterday4[name.D_INCREASE] = 0
                yesterday4[name.AMPLITUDE] = 0

            yma5 = values.loc[name.CLOSE][1:6].mean().round(2)
            yma10 = values.loc[name.CLOSE][1:11].mean().round(2)
            yma20 = values.loc[name.CLOSE][1:21].mean().round(2)

            yyma5 = values.loc[name.CLOSE][2:7].mean().round(2)
            yyma10 = values.loc[name.CLOSE][2:12].mean().round(2)
            yyma20 = values.loc[name.CLOSE][2:22].mean().round(2)

            yup = round(yma20 + (2 * round(np.std(values.loc[name.CLOSE][1:21]), 2)), 2)
            ydo = round(yma20 + (-2 * round(np.std(values.loc[name.CLOSE][1:21]), 2)), 2)

            yyup = round(yma20 + (2 * round(np.std(values.loc[name.CLOSE][2:22]), 2)), 2)
            yydo = round(yma20 + (-2 * round(np.std(values.loc[name.CLOSE][2:22]), 2)), 2)

            if yyesterday[name.VOLUME] > 0:
                yv = round(yesterday[name.VOLUME] / yyesterday[name.VOLUME], 1)
            else:
                yv = 0

            open = value.loc[name.OPEN]
            open_m = open * 1000
            open_fee = round((open_m * 0.001425) * (6 / 10))
            tax = open_m * 0.0015
            open_t = open_m - open_fee - tax

            close = value.loc[name.CLOSE]
            close_m = close * 1000
            close_fee = round((close_m * 0.001425) * (6 / 10))
            close_t = (close_m + close_fee) * -1

            d1.append([
                v[name.CODE],
                v[name.NAME],
                v[name.DATE],
                round(((open_t / -close_t) - 1) * 100, 2),

                value[name.OPEN],
                value[name.CLOSE],
                value[name.HIGH],
                value[name.LOW],
                value[name.VOLUME],
                value[name.INCREASE],
                value[name.D_INCREASE],
                value[name.AMPLITUDE],

                yesterday[name.OPEN],
                yesterday[name.CLOSE],
                yesterday[name.HIGH],
                yesterday[name.LOW],
                yesterday[name.VOLUME],
                yesterday[name.INCREASE],
                yesterday[name.D_INCREASE],
                yesterday[name.AMPLITUDE],
                data.get_max_v2(yyesterday[name.CLOSE]),

                yyesterday[name.OPEN],
                yyesterday[name.CLOSE],
                yyesterday[name.HIGH],
                yyesterday[name.LOW],
                yyesterday[name.VOLUME],
                yyesterday[name.INCREASE],
                yyesterday[name.D_INCREASE],
                yyesterday[name.AMPLITUDE],

                yesterday3[name.OPEN],
                yesterday3[name.CLOSE],
                yesterday3[name.HIGH],
                yesterday3[name.LOW],
                yesterday3[name.VOLUME],
                yesterday3[name.INCREASE],
                yesterday3[name.D_INCREASE],
                yesterday3[name.AMPLITUDE],

                yesterday4[name.OPEN],
                yesterday4[name.CLOSE],
                yesterday4[name.HIGH],
                yesterday4[name.LOW],
                yesterday4[name.VOLUME],
                yesterday4[name.INCREASE],
                yesterday4[name.D_INCREASE],
                yesterday4[name.AMPLITUDE],

                yma5,
                yma10,
                yma20,
                yyma5,
                yyma10,
                yyma20,

                # 60日最高價
                values.iloc[:, 2:62].loc[name.HIGH].max(),

                # 布林下通
                yup,
                # 布林上通
                ydo,
                # 布林寬度
                round(((yup / ydo) - 1) * 100, 1),
                round(((yyup / yydo) - 1) * 100, 1),
                # 5,10 ma相差
                round((pd.Series([yma5, yma10]).max() / pd.Series([yma5, yma10]).min() - 1) * 100, 1),
                # 10,20 ma相差
                round((pd.Series([yma10, yma20]).max() / pd.Series([yma10, yma20]).min() - 1) * 100, 1),
                # 5,10,20 ma相差
                round((pd.Series([yma5, yma10, yma20]).max() / pd.Series([yma5, yma10, yma20]).min() - 1) * 100, 1),
                # 5,20 ma相差
                round((pd.Series([yma5, yma20]).max() / pd.Series([yma5, yma20]).min() - 1) * 100, 1),
                # 昨量比
                yv,
                # 5日均量比
                round(yesterday[name.VOLUME] / values.loc[name.VOLUME][1:6].mean(), 1),
                # 10日均量比
                round(yesterday[name.VOLUME] / values.loc[name.VOLUME][1:11].mean(), 1),
                # 20日均量比
                round(yesterday[name.VOLUME] / values.loc[name.VOLUME][1:21].mean(), 1)
            ])

        except Exception as e:
            pass

    pd.DataFrame(d1, columns=columns).to_csv(
        os.path.join(os.path.dirname(path), 'data.csv'),
        encoding='utf-8-sig',
        index=False
    )


def CodeToDirCsv(path):
    for i, v in pd.read_csv(path).iterrows():
        if v[name.DATE] not in d:
            d[v[name.DATE]] = []

        d[v[name.DATE]].append([
            v[name.CODE],
            v[name.NAME],
            v[name.DATE],
        ])

    for k, v in d.items():
        dir = os.path.join(os.path.dirname(path), f'{k[:4]}{k[5:7]}')
        os.path.join(dir, f"{k}.csv")
        if os.path.exists(dir) == False:
            os.mkdir(dir)

        pd.DataFrame(v, columns=[name.CODE, name.NAME, name.DATE]).to_csv(
            os.path.join(dir, f"{k}.csv"),
            encoding='utf-8-sig',
            index=False
        )


def To01Dir(path):
    a = {}
    b = {}
    for i, v in pd.read_csv(path).iterrows():
        if v['m'] > 0:
            if v['date'] not in a:
                a[v['date']] = []

            a[v['date']].append(v.tolist())
        else:
            if v['date'] not in b:
                b[v['date']] = []

            b[v['date']].append(v.tolist())

    for k, v in a.items():
        dir = os.path.join(os.path.dirname(path), '1', f'{k[:4]}{k[5:7]}')
        if os.path.exists(dir) == False:
            os.mkdir(dir)

        pd.DataFrame(v, columns=[name.CODE, name.NAME, name.DATE, 'm']).to_csv(
            os.path.join(dir, f"{k}.csv"),
            encoding='utf-8-sig',
            index=False
        )

    for k, v in b.items():
        dir = os.path.join(os.path.dirname(path), '0', f'{k[:4]}{k[5:7]}')
        if os.path.exists(dir) == False:
            os.mkdir(dir)

        pd.DataFrame(v, columns=[name.CODE, name.NAME, name.DATE, 'm']).to_csv(
            os.path.join(dir, f"{k}.csv"),
            encoding='utf-8-sig',
            index=False
        )


def ToDirM(path):
    for i, v in pd.read_csv(path).iterrows():
        if v['m'] > 1:
            if v['date'] not in d:
                d[v['date']] = []

            d[v['date']].append(v.tolist()[:3])

    dir = os.path.join(os.path.dirname(path), 'm大於1')

    for k, v in d.items():
        pd.DataFrame(v, columns=[name.CODE, name.NAME, name.DATE]).to_csv(
            os.path.join(dir, f"{k}.csv"),
            encoding='utf-8-sig',
            index=False
        )


ToDirM("D:\\data\\csv\\strategy\\weak\\all\\data.csv")

# ToData("D:\\data\\csv\\strategy\\weak\\all\\code.csv")

f = 0
