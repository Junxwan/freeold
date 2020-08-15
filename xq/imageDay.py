import os
import time
import pyautogui
from . import item

class image(item.image):

    def screen(self, i, dir):
        # 1. 點擊技術分析
        # 2. 等待
        # 3. 截取技術分析圖
        pyautogui.click(450, 130)
        time.sleep(1)
        pyautogui.screenshot(os.path.join(dir, 'A-' + str(i) + '.png'), region=(75, 150, 1865, 970))

        # 1. 點擊走勢圖
        # 2. 等待
        # 3. 截取走勢圖
        pyautogui.click(180, 130)
        time.sleep(1)
        pyautogui.screenshot(os.path.join(dir, 'B-' + str(i) + '.png'), region=(75, 150, 1865, 970))
