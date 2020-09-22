import glob
import os
import time
import win32con
from datetime import datetime

import pandas as pd
import pyautogui
import win32gui

from stock import data as d

pyautogui.FAILSAFE = True


class Tick():
    def __init__(self, dir, csv_dir):
        self.dir = dir
        self.code = []
        self.date = []
        self.csv_dir = csv_dir
        self.windown_name = {}

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
            d_date = [d[0] for d in pd.read_csv(date, index_col=False, header=None).to_numpy().tolist()]

            for date in d_date:
                if self._get(date, c_data[c_data.columns[0]]) == False:
                    return False

            return True
        elif (code != '') & (os.path.isfile(date)):
            return self._get_date(code, [
                d[0] for d in pd.read_csv(date, index_col=False, header=None).to_numpy().tolist()
            ])

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

    def _get_date(self, code, dates) -> bool:
        year = datetime.now().year
        month = datetime.now().month

        for date in dates:
            self.move_date(date, year=year, month=month)
            time.sleep(2)

            if self._get(date, [code]) == False:
                return False

            year = int(date[:4])
            month = int(date[5:7])

        return True

    def _get(self, date, codes) -> bool:
        csv = os.path.join(self.csv_dir, date)

        i = 0
        for code in codes:
            name = f'{date}-{code}'
            file = os.path.join(self.dir, name) + '.xlsx'

            if (os.path.exists(file)) | (os.path.exists(os.path.join(csv, str(code)) + '.csv')):
                continue

            self.get(str(code), name)

            i += 1

            if i % 10 == 0:
                self.close_execl()

            if os.path.exists(file) == False:
                pyautogui.alert(
                    text=f'失敗:{file}',
                    title='結果',
                    button='OK'
                )

                return False

        return True

    def close_execl(self):
        self.windown_name = {}
        win32gui.EnumWindows(self.get_all_hwnd, 0)

        for index, name in self.windown_name.items():
            if len(name.split('Excel')) == 2:
                win32gui.PostMessage(index, win32con.WM_QUIT, 0, 0)

    def get_all_hwnd(self, hwnd, mouse):

        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            self.windown_name.update({hwnd: win32gui.GetWindowText(hwnd)})
