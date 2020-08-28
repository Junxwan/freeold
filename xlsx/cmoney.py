import codecs
import glob
import json
import logging
import os
import openpyxl
import csv
import pandas as pd
from stock import data as dt


def files(path):
    paths = []

    if os.path.isfile(path):
        paths.append(path)

    if os.path.isdir(path):
        for f in os.listdir(path):
            fullPath = os.path.join(path, f)

            if os.path.splitext(fullPath)[-1] == '.xlsx':
                paths.append(fullPath)

    return paths


# 個股基本資料
class stock():
    def __init__(self, file):
        xlsx = openpyxl.load_workbook(file)
        sheet = xlsx.active
        self.__data = {}

        for rows in sheet.iter_rows(2, 0, 0, sheet.max_column):
            self.__data[rows[0].value] = {
                'code': rows[0].value,
                'name': rows[1].value,
                'value': rows[2].value,
                'industryName': rows[3].value,
                'industryCode': rows[4].value,
                'industryIndexName': rows[5].value,
                'industrySubName': rows[6].value,
                'on': rows[7].value,
                'twsDate': rows[8].value,
                'otcDate': rows[9].value,
                'openDate': rows[10].value,
            }

    def output(self, path):
        f = codecs.open(os.path.join(path, 'cmoney-stock.json'), 'w+', 'utf-8')
        f.write(json.dumps(self.__data, ensure_ascii=False))
        f.close()


# 每日個股行情
class day():
    data = {}
    column = [dt.OPEN, dt.CLOSE, dt.HIGH, dt.LOW, dt.INCREASE, dt.AMPLITUDE, dt.VOLUME]
    dirs = {
        dt.OPEN: 'price',
        dt.CLOSE: 'price',
        dt.HIGH: 'price',
        dt.LOW: 'price',
        dt.INCREASE: 'price',
        dt.AMPLITUDE: 'price',
        dt.VOLUME: 'volume',
    }

    def __init__(self, file):
        logging.info('read: ' + file + ' ...')

        self.date = os.path.basename(file).split('.')[0]

        for i, rows in pd.read_excel(file).iterrows():
            for ii, value in enumerate(rows[2:]):
                d = rows.index[ii + 2]
                date = d[:4] + '-' + d[4:6] + '-' + d[6:8]

                if self.column[ii] not in self.data:
                    self.data[self.column[ii]] = []

                self.data[self.column[ii]].append({
                    'date': date,
                    'code': rows[0],
                    'value': value
                })

    def output(self, path):
        for name, value in self.data.items():
            os.path.join(path, self.dirs[name], name, )

        logging.info('total: ' + str(self.dirs.__len__()))


# 每年個股行情
class year():
    data = {}

    def __init__(self, path):
        self.path = path

        dirs = []

        if os.path.isdir(path):
            dirs = [x[0] for x in os.walk(path)]
        elif os.path.isfile(path):
            dirs = [os.path.dirname(path)]

        for dir in dirs:
            for file in glob.glob(dir + '/*.xlsx'):
                logging.info('read: ' + file + ' ...')

                for i, rows in pd.read_excel(file).iterrows():
                    for ii, value in enumerate(rows[2:]):
                        d = rows.index[ii + 2]
                        date = d[:4] + '-' + d[4:6] + '-' + d[6:8]

                        if dir not in self.data:
                            self.data[dir] = {}

                        if date not in self.data[dir]:
                            self.data[dir][date] = []

                        self.data[dir][date].append({
                            'date': date,
                            'code': rows[0],
                            'value': value
                        })

    def output(self, path):
        total = 0

        for input, item in self.data.items():
            dir = os.path.join(
                path,
                input.replace(self.path, '')[1:]
            )

            for date, value in item.items():
                fileDir = os.path.join(dir, date[:4] + date[5:7])

                if os.path.exists(fileDir) == False:
                    os.makedirs(fileDir)

                file = os.path.join(fileDir, date) + '.json'

                logging.info('file: ' + file)

                f = codecs.open(file, 'w+', 'utf-8')
                f.write(json.dumps(value, ensure_ascii=False))
                f.close()

                total += 1

        return total


# 每日弱勢股
# 成交量1000張以上
# 最大漲跌%3以上
# 最多100檔
# 收黑k
# 開盤價10元以上
class weakDay():
    __price = []

    def __init__(self, path):
        for path in files(path):
            xlsx = openpyxl.load_workbook(path)
            sheet = xlsx.active

            header = sheet.cell(1, 3).value
            self.__price.append({
                'date': f'{header[:4]}-{header[4:6]}-{header[6:8]}',
                'value': self.__read(sheet),
            })

    def __read(self, sheet):
        price = []

        for rows in sheet.iter_rows(2):
            if (rows[0].value == None) | (rows[0].value == ''):
                continue

            if (rows[8].value == None) | (rows[8].value == ''):
                continue

            # 股價小於10
            if rows[2].value < 10:
                continue

            # 成交小於1000張
            if rows[8].value <= 1000:
                continue

            diff = round(((rows[4].value / rows[5].value) - 1) * 100, 2)

            # 最大漲跌小於3
            if diff <= 3:
                continue

            # 收黑
            if rows[6].value >= 0:
                continue

            p = []
            for v in rows:
                p.append(v.value)

            p.append(diff)
            price.append(p)

        return sorted(price, key=lambda s: s[9], reverse=True)[:110]

    def output(self, path):
        for price in self.__price:
            codes = []
            date = price['date']
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
