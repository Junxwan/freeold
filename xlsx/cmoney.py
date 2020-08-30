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

        logging.info('total: ' + str(self.dirs.__len__()))


# 每年個股行情
class year():
    columns = dt.COLUMNS
    data = {}

    def __init__(self, path):
        self.data = {}
        self.path = path
        years = [os.path.basename(f).split('.')[0] for f in glob.glob(os.path.join(path, dt.OPEN, '*.xlsx'))]

        for year in years:
            for column in self.columns:
                file = os.path.join(path, column, f'{year}.xlsx')

                logging.info(f'read: {file}...')

                for i, rows in pd.read_excel(file).iterrows():
                    for ii, value in enumerate(rows[2:]):
                        if pd.isna(value):
                            continue

                        code = rows[0]
                        d = rows.index[ii + 2]
                        date = d[:4] + '-' + d[4:6] + '-' + d[6:8]

                        if code not in self.data:
                            self.data[code] = {}

                        if date not in self.data[code]:
                            self.data[code][date] = []

                        self.data[code][date].append(value)

    def output(self, path):
        data = {}

        for code, item in self.data.items():
            dir = os.path.join(path, str(code))

            if os.path.exists(dir) == False:
                os.mkdir(dir)

            for date, value in item.items():
                m = f'{date[:4]}{date[5:7]}'

                if m not in data:
                    data[m] = {}

                value.insert(0, date)

                if code not in data[m]:
                    data[m][code] = []

                data[m][code].append(value)

        columns = self.columns.copy()
        columns.insert(0, 'date')

        logging.info('save start')

        for date, item in data.items():
            for code, value in item.items():
                code = str(code)
                pd.DataFrame(value, columns=columns).to_excel(
                    os.path.join(path, code, f'{date}.xlsx'),
                    sheet_name=code,
                    index=False
                )

                logging.info(f'save {date} code: {code}')

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
