from stock import name, data
import codecs
import glob
import json
import logging
import os
import openpyxl
import pandas as pd
import numpy as np


def ToYear(path, toPath):
    dd = {}

    for p in glob.glob(os.path.join(path, "*.csv")):
        code = os.path.basename(p).split('.')[0]
        d = pd.read_csv(p)
        c = d.columns.tolist()[1:]

        for i, rows in d.iterrows():
            date = f"{str(rows[name.DATE])[:4]}-{str(rows[name.DATE])[4:6]}-{str(rows[name.DATE])[6:8]}"

            for cc in c:
                if cc not in dd:
                    dd[cc] = {}

                if date not in dd[cc]:
                    dd[cc][date] = []

                dd[cc][date].append([code, rows[cc]])

    for cc, v in dd.items():
        for date, vv in v.items():
            dir = os.path.join(os.path.abspath(toPath), cc.rstrip(), date[:4])

            if os.path.exists(dir) == False:
                os.makedirs(dir)

            file = os.path.join(dir, f"{date}.csv")

            if os.path.exists(file):
                continue

            pd.DataFrame(vv, columns=['code', 'value']).to_csv(file, index=False)

            logging.info(f'save {cc} {date}')
