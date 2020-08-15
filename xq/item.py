import math
import time

import pyautogui

PAGE_TOTAL = 20

pyautogui.FAILSAFE = True

def run(total, dir, image):
    now = time.time()
    count = total / PAGE_TOTAL
    max = math.ceil(count)

    for i in range(0, max):
        start = 0
        down = PAGE_TOTAL

        if (i == max - 1) & (count != max):
            start = PAGE_TOTAL - (total % PAGE_TOTAL)
            down = (total % PAGE_TOTAL)

        # 截圖並且將自選股移動至下一頁(每20筆一頁)
        for c in range(start, PAGE_TOTAL):
            pyautogui.click(2150, 270 + (c * 43))
            time.sleep(0.5)
            image.screen(c + (PAGE_TOTAL * i), dir)
            time.sleep(0.5)

        pyautogui.click(2150, 255 + (19 * 43))
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
