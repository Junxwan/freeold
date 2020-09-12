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
        self.ticks = {}

        tick_files = glob.glob(os.path.join(dir, '*.json'))
        if len(tick_files) == 0:
            for dir in glob.glob(os.path.join(dir, '*')):
                if os.path.isdir(dir):
                    self.ticks[os.path.basename(dir)] = glob.glob(os.path.join(dir, '*.json'))
        else:
            self.ticks[os.path.basename(dir)] = tick_files

    def output(self, output):
        name = os.path.basename(self.dir)
        output = os.path.join(output, name)
        if os.path.exists(output) == False:
            os.mkdir(output)

        self.to_csv(output)

    def to_csv(self, output):
        pass


class StockToCsv(ToCsv):
    def to_csv(self, output):
        for date, paths in self.ticks.items():
            stock = {}

            for path in paths:
                data = json.load(codecs.open(path, 'r', 'utf-8-sig'))

                if data['date'] != date:
                    return

                stock[data['code']] = data['tick']

            codes = sorted(list(stock.keys()))

            data = {}
            for i in range(266):
                values = []

                for c in codes:
                    if len(stock[c]) <= i:
                        [values.append(np.nan) for _ in self.columns]
                    else:
                        [values.append(v) for n, v in stock[c][i].items()]

                data[i] = values

            index = pd.MultiIndex.from_product([codes, self.columns], names=['code', 'name'])

            name = os.path.join(output, date) + '.csv'
            pd.DataFrame(data, index=index).to_csv(name)

            logging.info(f'save {name}')
