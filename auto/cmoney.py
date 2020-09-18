import glob
import os
import time
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
        pyautogui.write(name)
        pyautogui.press('enter')
        time.sleep(8)

        # 關閉execl
        pyautogui.keyDown('ALT')
        pyautogui.press('F4')
        pyautogui.keyUp('ALT')
        pyautogui.press('n')

    def move_date(self, date):
        (m, x, y) = d.calendar_xy(date)

        pyautogui.click(3630, 360)
        time.sleep(0.1)
        if m > 0:
            pyautogui.click(3300, 480, m)
            time.sleep(m * 0.1)

        pyautogui.click(3255 + (75 * x), 532 + (48 * y))

    def run(self, code, date):
        if os.path.isdir(date):
            self._get_dir(date)
        else:
            self._get_file(code, date)

    def _get_file(self, code, date):
        if code != '':
            if os.path.isfile(code):
                data = pd.read_csv(code, index_col=False, header=None)
                self.code = data[data.columns[0]]
            else:
                self.code.append(code)

            if os.path.isfile(date):
                data = pd.read_csv(date, index_col=False, header=None)
                self.date = data[data.columns[0]]
            else:
                self.date.append(date)
        elif os.path.isfile(date):
            self.date.append(os.path.basename(date).split('.')[0])
            self.code = pd.read_csv(date)['code']

        for d in self.date:
            self.move_date(d)
            time.sleep(0.5)

            for c in self.code:
                name = f'{d}-{c}'
                file = os.path.join(self.dir, name) + '.xlsx'

                if os.path.exists(file):
                    continue

                self.get(str(c), name)

                if os.path.exists(file) == False:
                    pyautogui.alert(
                        text=f'失敗:{file}',
                        title='結果',
                        button='OK'
                    )
                    return

    def _get_dir(self, dir):
        for path in glob.glob(os.path.join(dir, '*')):
            date = os.path.basename(path).split('.')[0]

            self.move_date(date)
            time.sleep(0.5)

            for code in pd.read_csv(path)['code']:
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
                    return
