import math
import time

import pyautogui

pyautogui.FAILSAFE = True


def run(total, dir, image):
    pageTotal = image.total()
    now = time.time()
    count = total / pageTotal
    max = math.ceil(count)

    for i in range(0, max):
        start = 0
        down = pageTotal

        if (i == max - 1) & (count != max):
            start = pageTotal - (total % pageTotal)
            down = (total % pageTotal)

        # 截圖並且將自選股移動至下一頁(每20筆一頁)
        for c in range(start, pageTotal):
            pyautogui.click(2150, 270 + (c * 43))
            time.sleep(0.5)
            image.screen(c + (pageTotal * i), dir)
            time.sleep(0.5)

        pyautogui.click(2150, 255 + ((pageTotal - 1) * 43))
        pyautogui.press('numlock')
        pyautogui.press('down', down)
        pyautogui.press('numlock')

        if (i != max - 1):
            time.sleep(10)

    pyautogui.alert(
        text='完成:' + str(total) + ' 時間:' + str(int((time.time() - now) / 60)) + ' 分',
        title='結果',
        button='OK'
    )


class image():

    def screen(self, i, dir):
        pass

    def total(self):
        pass
