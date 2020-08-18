import math
import os
import time

import pyautogui

pyautogui.FAILSAFE = True


def run(total, dir, image):
    pageTotal = image.total()
    now = time.time()
    count = total / pageTotal

    if os.path.exists(dir) == False:
        os.mkdir(dir)

    if total < pageTotal:
        for i in range(0, total):
            image.run(str(i), i, dir)
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
                image.run(str(c + (pageTotal * i)), c, dir)

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


class image():

    def screenshot(self, name, dir):
        pass

    def run(self, name, offset, dir):
        pyautogui.click(2150, 270 + (offset * 43))
        time.sleep(0.5)
        self.screenshot(name, dir)
        time.sleep(0.5)

    def total(self):
        pass
