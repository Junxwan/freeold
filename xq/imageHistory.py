import os
import time
import pyautogui
from . import item


class image(item.image):
    def __init__(self, prevDay=0, prevMonth=0, dayX=1, dayY=1):
        self.__prevDay = prevDay
        self.__prevMonth = prevMonth
        self.__dayX = dayX
        self.__dayY = dayY

    def screen(self, name, dir):
        # 1. 點擊技術分析
        # 2. 往前移動幾日
        # 3. 截取技術分析圖
        pyautogui.click(450, 130)
        time.sleep(0.5)
        pyautogui.click(800, 1010, self.__prevDay)
        time.sleep(0.05 * self.__prevDay)
        pyautogui.screenshot(os.path.join(dir, 'A-' + str(name) + '.png'), region=(75, 150, 1865, 890))

        # 1. 點擊走勢圖
        # 2. 點擊日期menu
        # 3. 往前幾月
        # 4. 點擊日期
        # 3. 截取走勢圖
        pyautogui.click(180, 130)
        time.sleep(0.5)
        pyautogui.click(90, 220)
        pyautogui.click(100, 260, self.__prevMonth)
        time.sleep(0.5)
        pyautogui.click(42 + (53 * self.__dayX), 306 + (29 * self.__dayY))
        time.sleep(2)
        pyautogui.screenshot(os.path.join(dir, 'B-' + str(name) + '.png'), region=(75, 150, 1865, 890))

    def total(self):
        return 18
