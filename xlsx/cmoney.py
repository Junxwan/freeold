import codecs
import glob
import json
import logging
import os
from datetime import datetime

import openpyxl
import csv
import pandas as pd
import numpy as np
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

    def __init__(self, file):
        logging.info('read: ' + file + ' ...')

        self.date = os.path.basename(file).split('.')[0]

        for i, rows in pd.read_excel(file).iterrows():
            for ii, value in enumerate(rows[2:]):
                if pd.isna(value):
                    continue

                d = rows.index[ii + 2]

                if self.column[ii] not in self.data:
                    self.data[self.column[ii]] = []

                self.data[self.column[ii]].append({
                    'date': d[:8],
                    'code': rows[0],
                    'value': value
                })

    def output(self, path):
        data = {}
        m = f'{self.date[:4]}{self.date[5:7]}'
        columns = dt.COLUMNS.copy()
        columns.insert(0, 'date')

        for name, item in self.data.items():
            for value in item:
                code = value['code']
                if code not in data:
                    data[code] = [self.date]

                data[code].append(value['value'])

        for code, value in data.items():
            code = str(code)

            dir = os.path.join(path, code)

            if os.path.exists(dir) == False:
                os.makedirs(dir)

            f = os.path.join(dir, f'{m}.xlsx')

            insert = pd.DataFrame([value], columns=columns)

            if os.path.exists(f) == False:
                p = insert
            else:
                p = pd.read_excel(f).append(insert)
                p['date'] = pd.to_datetime(p['date'])
                p.sort_values(by=['date'], ascending=False, inplace=True)

            p['date'] = p['date'].dt.strftime('%Y-%m-%d')
            p.to_excel(f, sheet_name=code, index=False)

            logging.info(f'save file: {f}')


# 每年個股行情
class year():
    dataColumns = dt.COLUMNS
    columns = dataColumns.copy()

    def __init__(self, path):
        self.data = {}
        self.path = path
        self.columns.insert(0, dt.DATE)
        years = [os.path.basename(f).split('.')[0] for f in glob.glob(os.path.join(path, dt.OPEN, '*.xlsx'))]
        last = years[-1]

        for year in years:
            for column in self.dataColumns:
                file = os.path.join(path, column, f'{year}.xlsx')

                logging.info(f'read: {file}...')

                for i, rows in pd.read_excel(file).iterrows():
                    for ii, value in enumerate(rows[2:]):
                        if pd.isna(value):
                            continue

                        code = rows[0]
                        d = rows.index[ii + 2]
                        date = d[:4] + '-' + d[4:6] + '-' + d[6:8]

                        if year == last:
                            m = d[:6]
                        else:
                            m = year

                        if m not in self.data:
                            self.data[m] = {}

                        if date not in self.data[m]:
                            self.data[m][date] = {}

                        if code not in self.data[m][date]:
                            self.data[m][date][code] = {c: 0 for c in self.columns}
                            self.data[m][date][code][dt.DATE] = date

                        self.data[m][date][code][column] = value

    def output(self, path):
        logging.info('save start')

        for name, dates in self.data.items():
            i = 0
            data = {}
            filePath = os.path.join(path, name) + ".csv"
            ck = list(dates[list(dates.keys())[-1]].keys())
            index = pd.MultiIndex.from_product([ck, self.columns], names=['code', 'name'])

            for date, codes in dates.items():
                values = []

                for c in ck:
                    if c not in codes:
                        [values.append(np.nan) for n in self.columns]
                    else:
                        [values.append(v) for n, v in codes[c].items()]

                data[i] = values
                i += 1

            pd.DataFrame(data, index=index).to_csv(filePath)

            logging.info(f'save {name}')

        logging.info('save end')


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
