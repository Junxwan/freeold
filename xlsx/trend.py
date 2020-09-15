# -*- coding: utf-8 -*-

import codecs
import glob
import json
import logging
import os
import pandas as pd
import numpy as np


class ToCsv():
    columns = ['time', 'price', 'volume', 'max', 'min']

    def __init__(self, dir):
        self.dir = dir
        self.trends = {}

        trend_files = glob.glob(os.path.join(dir, '*.json'))
        if len(trend_files) == 0:
            for dir in glob.glob(os.path.join(dir, '*')):
                if os.path.isdir(dir):
                    self.trends[os.path.basename(dir)] = glob.glob(os.path.join(dir, '*.json'))
        else:
            self.trends[os.path.basename(dir)] = trend_files

    def output(self, output):
        name = os.path.basename(self.dir)
        output = os.path.join(output, name)
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
        stock = {}

        for path in paths:
            data = json.load(codecs.open(path, 'r', 'utf-8-sig'))

            if data['date'] != date:
                return

            stock[data['code']] = data['tick']

        codes = sorted(list(stock.keys()))

        data = {}
        for i in range(270):
            values = []

            for c in codes:
                if len(stock[c]) <= i:
                    [values.append(np.nan) for _ in self.columns]
                else:
                    for n, v in stock[c][i].items():
                        if n == 'time':
                            v = pd.Timestamp(v, unit='s')
                        values.append(v)

            data[i] = values

        index = pd.MultiIndex.from_product([codes, self.columns], names=['code', 'name'])
        name = os.path.join(output, date) + '.csv'
        pd.DataFrame(data, index=index).to_csv(name)

        logging.info(f'save {name}')


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
