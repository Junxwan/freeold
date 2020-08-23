import csv
import logging
import os
import openpyxl
from . import data


def run(date, dir, outputPath):
    stock = data.stock(dir)

    dates = []
    if os.path.isdir(date):
        for f in os.listdir(date):
            n = os.path.splitext(f)

            if n[-1] != '.xlsx':
                continue

            dates.append(n[0])
    else:
        dates.append(date)

    for date in dates:
        output(list(date, stock), date, outputPath)


def list(date, stock):
    price = []

    for code in stock.codes(date):
        name = code['name']
        code = code['code']

        open, close, max, min, increase, amplitude, volume = stock.code(code, date, keyName=True)

        # 股價小於10
        if open[0] <= 10:
            continue

        # 成交小於1000張
        if volume[0] <= 1000:
            continue

        diff = round(((max[0] / min[0]) - 1) * 100, 2)

        # 最大漲跌小於3
        if diff <= 3:
            continue

        # 收黑
        if increase[0] >= 0:
            continue

        if open[0] <= close[0]:
            continue

        price.append([name, code, open[0], close[0], max[0], min[0], increase[0], amplitude[0], volume[0], diff])

    return sorted(price, key=lambda s: s[9], reverse=True)[:110]


def output(prices, date, path):
    ws = openpyxl.Workbook()
    wsM = ws.active
    xlsxPath = os.path.join(path, f'{date}.xlsx')
    csvPath = os.path.join(path, f'{date}-code.csv')

    wsM.append([
        '股票代號',
        '股票名稱',
        f'{date}\n開盤價',
        f'{date}\n收盤價',
        f'{date}\n最高價',
        f'{date}\n最低價',
        f'{date}\n漲幅(%)',
        f'{date}\n振幅(%)',
        f'{date}\n成交量',
        f'{date}\n最大漲跌(%)'
    ])

    for p in prices:
        wsM.append(p)

    ws.save(xlsxPath)

    with open(csvPath, 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile)

        for code in [f'{c[1]}.TW' for c in prices]:
            writer.writerow([code])

    logging.info(xlsxPath)
    logging.info(csvPath)
