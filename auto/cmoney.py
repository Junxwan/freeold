import os
import time

import pandas as pd
import pyautogui

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

    def run(self, code, date):
        if os.path.isfile(code):
            data = pd.read_excel(code)
            self.code = data[data.columns[0]]
        else:
            self.code.append(code)

        if os.path.isfile(date):
            data = pd.read_excel(date)
            self.date = data[data.columns[0]]
        else:
            self.date.append(date)

        for d in date:
            for c in code:
                name = f'{d}-{c}'
                self.get(code, name)
                file = os.path.join(self.dir, name) + '.xls'

                if os.path.exists(file) == False:
                    pyautogui.alert(
                        text=f'失敗:{file}',
                        title='結果',
                        button='OK'
                    )
                    return
