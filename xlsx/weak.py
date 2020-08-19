import csv
import logging
import os

import openpyxl

from xlsx import data


def run(date, dir):
    price = []
    stock = data.stock(dir)

    for code in stock.codes(date):
        name = code['name']
        code = code['code']

        open, close, max, min, increase, amplitude, volume = stock.code(code, date, keys=['open'], keyName=True)

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

        price.append([name, code, open[0], close[0], max[0], min[0], increase[0], amplitude[0], volume[0], diff])

    output(price, date, dir)


def output(prices, date, path):
    for price in prices:
        codes = []
        ws = openpyxl.Workbook()
        wsM = ws.active

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

        for p in price['value']:
            codes.append([f'{p[0]}.TW'])
            wsM.append(p)

        xlsxPath = os.path.join(path, f'{date}.xlsx')
        csvPath = os.path.join(path, f'{date}-code.csv')
        ws.save(xlsxPath)

        with open(csvPath, 'w+', newline='') as csvfile:
            writer = csv.writer(csvfile)

            for code in codes:
                writer.writerow(code)

        logging.info(xlsxPath)
        logging.info(csvPath)


run('2020-08-14', '/private/var/www/other/free')
