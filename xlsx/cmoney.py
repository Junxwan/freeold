import codecs
import json
import logging
import os
import openpyxl
import csv


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
    __data = {}
    __column = ['open', 'close', 'max', 'min', 'increase', 'amplitude', 'volume']
    __path = {
        'open': 'price',
        'close': 'price',
        'max': 'price',
        'min': 'price',
        'increase': 'price',
        'amplitude': 'price',
        'volume': 'volume',
    }

    def __init__(self, file):
        logging.info('read: ' + file + ' ...')
        xlsx = openpyxl.load_workbook(file)
        sheet = xlsx.active

        row = sheet.cell(1, 3).value
        self.__m = row[:6]
        self.__date = row[:4] + '-' + row[4:6] + '-' + row[6:8]

        for c in self.__column:
            self.__data[c] = {}

        for rows in sheet.iter_rows(2, 0, 0, sheet.max_column):
            for index, row in enumerate(rows[2:]):
                if (rows[0].value == None) | (rows[1].value == None):
                    continue

                value = row.value
                if value == '':
                    value = 0

                self.__data[self.__column[index]][rows[0].value] = {
                    'name': rows[1].value,
                    'value': value,
                }

    def output(self, path):
        for name, dName in self.__path.items():
            dir = os.path.join(path, dName, name, self.__m)
            os.makedirs(dir, exist_ok=True)

            filePath = os.path.join(dir, self.__date) + ".json"

            f = codecs.open(filePath, 'w+', 'utf-8')
            f.write(json.dumps({
                'date': self.__date,
                'value': self.__data[name],
            }, ensure_ascii=False))
            f.close()

            logging.info('save ' + name + ' ' + filePath)

        logging.info('total: ' + str(self.__path.__len__()))


# 每年個股行情
class year():
    __data = []

    def __init__(self, path):
        for path in files(path):
            logging.info('read: ' + path + ' ...')
            xlsx = openpyxl.load_workbook(path)
            sheet = xlsx.active
            dates = []
            price = {}

            for rows in sheet.iter_rows(0, 1, 0, sheet.max_column):
                for row in rows[2:]:
                    date = row.value[:4] + '-' + row.value[4:6] + '-' + row.value[6:8]
                    dates.append(date)

                    if price.get(row.value[:6]) == None:
                        price[row.value[:6]] = {}

                    if price[row.value[:6]].get(date) == None:
                        price[row.value[:6]][date] = {}

            for rows in sheet.iter_rows(2, 0, 0, sheet.max_column):
                for index, row in enumerate(rows[2:]):
                    date = dates[index]

                    if (rows[0].value == None) | (rows[1].value == None):
                        continue

                    value = row.value
                    if value == '':
                        value = 0

                    price[date[:4] + date[5:7]][date][rows[0].value] = {
                        'name': rows[1].value,
                        'value': value,
                    }

            self.__data.append({
                'path': path,
                'price': price,
            })

    def output(self, path):
        total = 0
        for data in self.__data:
            for name, month in data['price'].items():
                dir = os.path.join(path, name)

                if os.path.exists(dir) == False:
                    os.mkdir(dir)

                logging.info('source xlsx: ' + data['path'])
                logging.info('output path: ' + dir)

                for date, value in month.items():
                    file = os.path.join(dir, date) + ".json"

                    if os.path.exists(file):
                        continue

                    f = codecs.open(file, 'w+', 'utf-8')
                    f.write(json.dumps({
                        'date': date,
                        'value': value,
                    }, ensure_ascii=False))
                    f.close()

                    total += 1
                    logging.info('date: ' + date)

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
