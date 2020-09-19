import glob
import os
import time
from datetime import datetime

import pandas as pd
import pyautogui
from stock import data as d

pyautogui.FAILSAFE = True


class Tick():
    def __init__(self, dir):
        self.dir = dir
        self.code = []
        self.date = []

    def get(self, code, name):
        # 選擇個股
        pyautogui.click(250, 240)
        pyautogui.write(code)
        pyautogui.press('enter')
        time.sleep(2)

        # 匯出
        pyautogui.click(3000, 1500, button='right')
        pyautogui.click(3050, 1580)
        time.sleep(0.5)
        pyautogui.write(name)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(9)

        # 關閉execl
        pyautogui.keyDown('ALT')
        pyautogui.press('F4')
        pyautogui.keyUp('ALT')
        pyautogui.press('n')
        time.sleep(1)

    def move_date(self, date, year=None, month=None):
        (m, x, y) = d.calendar_xy(date, year, month)

        pyautogui.click(3630, 360)
        time.sleep(1)
        if m > 0:
            pyautogui.click(3300, 480, m)
            time.sleep(m * 1)

        pyautogui.click(3255 + (75 * x), 532 + (48 * y))

    def run(self, code, date):
        # 根據單一檔案 <path>/2020-08-14.csv
        if (code == '') & os.path.isfile(date):
            return self._get_file(date)

        # 　根據目錄檔案　<path>/2020-08-14.csv　<path>/2020-08-13.csv
        elif os.path.isdir(date):
            return self._get_dir(date)

        # 根據code與date檔案清單
        elif os.path.isfile(code) & os.path.isfile(date):
            c_data = pd.read_csv(code, index_col=False, header=None)
            d_date = pd.read_csv(date, index_col=False, header=None)

            for date in d_date:
                if self._get(date, c_data[c_data.columns[0]]) == False:
                    return False

            return True

        # 指定code與date
        elif (code != '') & (date != ''):
            return self._get([date], [code])

    def _get_dir(self, dir) -> bool:
        year = datetime.now().year
        month = datetime.now().month

        for path in sorted(glob.glob(os.path.join(dir, '*.csv')), reverse=True):
            date = os.path.basename(path).split('.')[0]

            self.move_date(date, year=year, month=month)
            time.sleep(2)

            if self._get(date, pd.read_csv(path)['code']) == False:
                return False

            year = int(date[:4])
            month = int(date[5:7])

        return True

    def _get_file(self, file) -> bool:
        date = os.path.basename(file).split('.')[0]
        self.move_date(date)
        time.sleep(2)

        return self._get(date, pd.read_csv(file)['code'])

    def _get(self, date, code) -> bool:
        for code in code:
            name = f'{date}-{code}'
            file = os.path.join(self.dir, name) + '.xlsx'

            if os.path.exists(file):
                continue

            self.get(str(code), name)

            if os.path.exists(file) == False:
                pyautogui.alert(
                    text=f'失敗:{file}',
                    title='結果',
                    button='OK'
                )

                return False

        return True
