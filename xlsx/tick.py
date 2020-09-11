import codecs
import glob
import json
import logging
import os
import pandas as pd
import numpy as np


class to_csv():
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

            file_dir = os.path.join(output, f'{date[:4]}{date[5:7]}')
            if os.path.exists(file_dir) == False:
                os.mkdir(file_dir)

            name = os.path.join(file_dir, date) + '.csv'
            pd.DataFrame(data, index=index).to_csv(name)

            logging.info(f'save {name}')
