# -*- coding: utf-8 -*-

import codecs
import glob
import json
import logging
import os
import pandas as pd
import numpy as np
from stock import name


class ToCsv():
    columns = [name.TIME, name.PRICE, name.VOLUME, 'max', 'min']

    def __init__(self, dir):
        self.dir = dir
        self.trends = {}

        trend_files = glob.glob(os.path.join(dir, '*.json'))
        if len(trend_files) == 0:
            for dir in sorted(glob.glob(os.path.join(dir, '*')), reverse=True):
                if os.path.isdir(dir):
                    self.trends[os.path.basename(dir)] = glob.glob(os.path.join(dir, '*.json'))
        else:
            self.trends[os.path.basename(dir)] = trend_files

    def output(self, output):
        name = os.path.basename(self.dir)
        output = os.path.join(output, name[:4])
        if os.path.exists(output) == False:
            os.makedirs(output)

        self.to_csv(output)

    def to_csv(self, output):
        pass


class StockToCsv(ToCsv):
    def to_csv(self, output):
        for date, paths in self.trends.items():
            self._to_csv(date, paths, output)

    def _to_csv(self, date, paths, output):
        columns = [name.TIME, name.PRICE, name.VOLUME, name.HIGH, name.LOW, name.CLOSE, name.OPEN, name.AVG]
        file = os.path.join(output, date) + '.csv'

        if os.path.exists(file):
            return

        stock = {}

        for path in paths:
            data = json.load(codecs.open(path, 'r', 'utf-8-sig'))

            if data['date'] != date:
                return

            stock[str(data['code'])] = data['tick']

        for code, rows in stock.items():
            max = rows[0]['max']
            min = rows[0]['min']
            stock[code][0][name.CLOSE] = rows[0][name.PRICE]
            stock[code][0][name.PRICE] = rows[0][name.PRICE]
            stock[code][0][name.OPEN] = np.nan
            stock[code][0][name.AVG] = np.nan

            for i, value in enumerate(rows[1:]):
                p = value[name.PRICE]

                if value['max'] > max:
                    max = value['max']
                    p = max
                elif value['min'] < min:
                    min = value['min']
                    p = min

                stock[code][i + 1][name.CLOSE] = value[name.PRICE]
                stock[code][i + 1][name.PRICE] = p
                stock[code][i + 1][name.OPEN] = np.nan
                stock[code][i + 1][name.AVG] = np.nan

        codes = sorted(list(stock.keys()))

        data = {}
        for i in range(270):
            values = []

            for c in codes:
                if len(stock[c]) <= i:
                    [values.append(np.nan) for _ in range(len(columns))]
                else:
                    for n, v in stock[c][i].items():
                        if n == 'time':
                            v = pd.Timestamp(v, unit='s')
                        values.append(v)

            data[i] = values

        pd.DataFrame(
            data,
            index=(pd.MultiIndex.from_product([codes, columns], names=['code', 'name']))
        ).to_csv(file)

        logging.info(f'save {file}')


class MarketToCsv(ToCsv):
    def to_csv(self, output):
        for date, paths in self.trends.items():
            for path in paths:
                self._to_csv(path, output)

    def _to_csv(self, file_path, output):
        data = json.load(codecs.open(file_path, 'r', 'utf-8-sig'))
        values = []

        for d in data['tick']:
            value = []
            for n, v in d.items():
                if n == 'time':
                    v = pd.Timestamp(v, unit='s')
                value.append(v)
            values.append(value)

        file = os.path.join(output, data['date']) + '.csv'
        pd.DataFrame(values, columns=self.columns).to_csv(file)
        logging.info(f'save {file}')
