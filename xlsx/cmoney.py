import codecs
import json
import logging
import os

import openpyxl


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
            self.__data[c] = []

        for rows in sheet.iter_rows(2, 0, 0, sheet.max_column):
            for index, row in enumerate(rows[2:]):
                self.__data[self.__column[index]].append({
                    'code': rows[0].value,
                    'name': rows[1].value,
                    'value': row.value,
                })

    def output(self, path):
        for name, dName in self.__path.items():
            dir = os.path.join(path, dName, name, self.__m)
            os.makedirs(dir, exist_ok=True)

            filePath = os.path.join(dir, self.__date) + ".json"

            if os.path.exists(filePath):
                continue

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
        paths = []

        if os.path.isfile(path):
            paths.append(path)

        if os.path.isdir(path):
            for f in os.listdir(path):
                fullPath = os.path.join(path, f)

                if os.path.splitext(fullPath)[-1] == '.xlsx':
                    paths.append(fullPath)

        for path in paths:
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
                        price[row.value[:6]][date] = []

            for rows in sheet.iter_rows(2, 0, 0, sheet.max_column):
                for index, row in enumerate(rows[2:]):
                    date = dates[index]
                    price[date[:4] + date[5:7]][date].append({
                        'code': rows[0].value,
                        'name': rows[1].value,
                        'value': row.value,
                    })

            self.__data.append({
                'path': path,
                'price': price,
            })

    def output(self, path):
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

                    logging.info('date: ' + date)
