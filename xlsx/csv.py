import os
import glob
import pandas as pd
import numpy as np
import logging
from stock import data, name


def ToCsv(path, toPath, year="*"):
    dd = {}
    codes = {}
    # stock = data.Stock(toPath)
    # stock.readAll()

    columns = [name.OPEN, name.CLOSE, name.HIGH, name.LOW, name.INCREASE, name.AMPLITUDE, name.VOLUME, name.DAY_VOLUME,
               name.MAIN, name.FUND, name.FOREIGN, name.VOLUME_5, name.VOLUME_10, name.VOLUME_20]

    dates = [os.path.basename(d).split('.')[0] for d in glob.glob(os.path.join(path, name.OPEN, '2021', "*.csv"))][::-1]

    try:
        for p in glob.glob(os.path.join(path, name.OPEN, "*", "*.csv")):
            for c in pd.read_csv(p)['code']:
                if c not in codes:
                    codes[c] = 1

        codes = list(codes)

        for date in dates:
            logging.info(f"read {date}")

            y = date[:4]

            if y not in dd:
                dd[y] = {}

            if date not in dd[y]:
                dd[y][date] = {}

            for c in columns:
                f = os.path.join(path, c, date[:4], f"{date}.csv")

                if os.path.exists(f):
                    for i, v in pd.read_csv(f).iterrows():
                        code = int(v['code'])
                        if code not in dd[y][date]:
                            dd[y][date][code] = {}
                            dd[y][date][code][name.DATE] = date

                        dd[y][date][code][c] = v['value']
                else:
                    for code in list(dd[y][date].keys()):
                        dd[y][date][code][c] = np.nan

    except Exception as e:
        logging.error(e.__str__())

    columns.insert(0, name.DATE)
    index = pd.MultiIndex.from_product([codes, columns], names=['code', 'name'])

    for year, v in dd.items():
        i = 0
        dd = {}

        for date, vv in v.items():
            values = []

            for code in codes:
                if code in vv:
                    for c in columns:
                        if c in vv[code]:
                            values.append(vv[code][c])
                        else:
                            values.append(0)
                else:
                    [values.append(np.nan) for _ in columns]

            dd[i] = values
            i += 1

        pd.DataFrame(dd, index=index).to_csv(os.path.join(path, toPath, f"{year}.csv"))

        logging.info(f'save {year}')
