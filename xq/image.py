import math
import os
import time

import pyautogui

pyautogui.FAILSAFE = True


class image():
    def start(self, total, dir):
        pageTotal = self.total()
        now = time.time()
        count = total / pageTotal
        index = 0

        if os.path.exists(dir) == False:
            os.mkdir(dir)

        if total < pageTotal:
            for i in range(0, total):
                self.run(str(i), i, dir)
        else:
            max = math.ceil(count)

            for i in range(0, max):
                start = 0
                down = pageTotal

                if (i == max - 1) & (count != max):
                    start = pageTotal - (total % pageTotal)
                    down = (total % pageTotal)

                # 截圖並且將自選股移動至下一頁(每20筆一頁)
                for c in range(start, pageTotal):
                    index += 1
                    self.run(str(index), c, dir)

                pyautogui.click(2150, 255 + ((pageTotal - 1) * 43))
                pyautogui.press('numlock')
                pyautogui.press('down', down)
                pyautogui.press('numlock')

                if (i != max - 1):
                    time.sleep(7)

        pyautogui.alert(
            text='完成:' + str(total) + ' 時間:' + str(int((time.time() - now) / 60)) + ' 分',
            title='結果',
            button='OK'
        )

    def screenshot(self, name, dir):
        pass

    def run(self, name, offset, dir):
        pyautogui.click(2150, 270 + (offset * 43))
        time.sleep(0.5)
        self.screenshot(name, dir)
        time.sleep(0.5)

    def total(self):
        return 0


class day(image):

    def screenshot(self, name, dir):
        # 1. 點擊技術分析
        # 2. 等待
        # 3. 截取技術分析圖
        pyautogui.click(470, 130)
        time.sleep(1)
        pyautogui.screenshot(os.path.join(dir, 'A-' + name + '.png'), region=(75, 150, 1865, 970))

        # 1. 點擊走勢圖
        # 2. 等待
        # 3. 截取走勢圖
        pyautogui.click(180, 130)
        time.sleep(1)
        pyautogui.screenshot(os.path.join(dir, 'B-' + name + '.png'), region=(75, 150, 1865, 970))

    def total(self):
        return 20


class history(image):
    def __init__(self, prevDay=0, prevMonth=0, dayX=1, dayY=1):
        self.__prevDay = prevDay
        self.__prevMonth = prevMonth
        self.__dayX = dayX
        self.__dayY = dayY

    def screenshot(self, name, dir):
        # 1. 點擊技術分析
        # 2. 往前移動幾日
        # 3. 截取技術分析圖
        pyautogui.click(470, 130)
        time.sleep(0.5)
        pyautogui.click(800, 1010, self.__prevDay)
        time.sleep(0.05 * self.__prevDay)
        pyautogui.screenshot(os.path.join(dir, 'A-' + name + '.png'), region=(75, 150, 1865, 890))

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
        pyautogui.screenshot(os.path.join(dir, 'B-' + name + '.png'), region=(75, 150, 1865, 890))

    def total(self):
        return 18
