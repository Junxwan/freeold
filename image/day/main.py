import argparse
import math
import time

import pyautogui

pyautogui.FAILSAFE = True


# parser = argparse.ArgumentParser()
#
# parser.add_argument('x', type=int)
# parser.add_argument('y', type=int)
# args = parser.parse_args()

def xqImage(i):
    # 1. 點擊技術分析
    # 2. 等待
    # 3. 截取技術分析圖
    pyautogui.click(350, 130)
    time.sleep(1)
    pyautogui.screenshot('A-' + str(i) + '.png', region=(75, 150, 1865, 970))

    # 1. 點擊走勢圖
    # 2. 等待
    # 3. 截取走勢圖
    pyautogui.click(200, 130)
    time.sleep(1)
    pyautogui.screenshot('B-' + str(i) + '.png', region=(75, 150, 1865, 970))


def scanImage(start=0):
    for i in range(start, 20):
        pyautogui.click(2150, 270 + (i * 43))
        # xqImage(i)
        time.sleep(0.5)


def run():
    total = 109
    count = total / 20
    max = math.ceil(count)

    for i in range(0, max):
        start = 0
        down = 20

        if (i == max - 1) & (count != max):
            start = 20 - (total % 20)
            down = (total % 20)

        # 截圖並且將自選股移動至下一頁(每20筆一頁)
        scanImage(start)
        pyautogui.click(2150, 255 + (19 * 43))
        pyautogui.press('numlock')
        pyautogui.press('down', down)
        pyautogui.press('numlock')
        time.sleep(10)

    pyautogui.alert(text='完成', title='結果', button='OK')


run()