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
        columns = [name.TIME, name.OPEN, name.CLOSE, name.VOLUME, name.HIGH, name.LOW, name.AVG]
        file = os.path.join(output, date) + '.csv'
        names = ['code', 'name']

        if os.path.exists(file):
            data_frame = pd.read_csv(file, index_col=[0, 1], header=[0], low_memory=False)
            file_codes = sorted(data_frame.index.levels[0].tolist())
            codes = sorted([int(os.path.basename(path).split('.')[0]) for path in paths])
            diff_codes = list(set(codes).difference(set(file_codes)))

            if len(diff_codes) == 0:
                return True

            path = os.path.dirname(paths[0])
            paths = [os.path.join(path, str(code)) + '.json' for code in diff_codes]

            add, codes = self._get(date, paths, columns)

            apply = pd.DataFrame(
                add,
                index=(pd.MultiIndex.from_product([[int(code) for code in codes], columns], names=names))
            )

            for index, rows in apply.iterrows():
                data_frame.loc[index, :] = rows.tolist()
        else:
            data, codes = self._get(date, paths, columns)
            data_frame = pd.DataFrame(
                data,
                index=(pd.MultiIndex.from_product([codes, columns], names=names))
            )

        data_frame.to_csv(file)
        logging.info(f'save {file}')

    def _get(self, date, paths, columns):
        stock = {}

        for path in paths:
            data = json.load(codecs.open(path, 'r', 'utf-8-sig'))

            if data['date'] != date:
                logging.error(f'{path} date is error')
                return None, None

            stock[str(data['code'])] = data['tick']

        for code, rows in stock.items():
            stock[code][0][name.OPEN] = np.nan
            stock[code][0][name.AVG] = np.nan

            for i, value in enumerate(rows[1:]):
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
                    for n in columns:
                        v = stock[c][i][n]
                        if n == 'time':
                            v = pd.Timestamp(v, unit='s')
                        values.append(v)

            data[i] = values

        return data, codes


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
