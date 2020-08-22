import calendar
import math
import os
import time
import pyautogui
from datetime import datetime
from stock import data

pyautogui.FAILSAFE = True

prevDays = {}


def calendarXY(date, dir):
    if date in prevDays:
        return prevDays[date]
    else:
        prevDays[date] = []

    prevDay = data.stock(dir).afterDates(date).__len__()

    dateT = datetime.fromisoformat(date)
    nM = datetime.now().month
    nY = datetime.now().year

    prevMonth = 0
    dayX = 1
    dayY = dateT.isocalendar()[1] % 6

    if nY != dateT.year:
        prevMonth += ((nY - dateT.year) * 12)

    if nM != dateT.month:
        prevMonth += abs(nM - dateT.month)

    if dateT.isocalendar()[2] != 7:
        dayX = dateT.isocalendar()[2] + 1

    weeks = calendar.Calendar(calendar.SUNDAY).monthdayscalendar(dateT.year, dateT.month)

    for index in range(weeks.__len__()):
        if dateT.day in weeks[index]:
            dayY = index + 1

    d = [prevDay, prevMonth, dayX, dayY]

    for v in d:
        prevDays[date].append(v)

    return d


class stock():
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


class stockNow(stock):
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


class stockHistory(stock):
    def __init__(self, date, dir):
        self.prevDay, self.prevMonth, self.dayX, self.dayY = calendarXY(date, dir)

    def screenshot(self, name, dir):
        # 1. 點擊技術分析
        # 2. 往前移動幾日
        # 3. 截取技術分析圖
        self.moveK()
        pyautogui.screenshot(os.path.join(dir, 'A-' + name + '.png'), region=(75, 150, 1865, 890))

        # 1. 點擊走勢圖
        # 2. 點擊日期menu
        # 3. 往前幾月
        # 4. 點擊日期
        # 3. 截取走勢圖
        self.moveTrend()
        pyautogui.screenshot(os.path.join(dir, 'B-' + name + '.png'), region=(75, 150, 1865, 890))

    def moveK(self):
        pyautogui.click(470, 130)
        time.sleep(0.5)
        pyautogui.click(800, 1010, self.prevDay)
        time.sleep(0.05 * self.prevDay)

    def moveTrend(self):
        pyautogui.click(180, 130)
        time.sleep(0.5)
        pyautogui.click(90, 220)
        pyautogui.click(100, 260, self.prevMonth)
        time.sleep(0.5)
        pyautogui.click(42 + (53 * self.dayX), 306 + (29 * self.dayY))
        time.sleep(2)

    def total(self):
        return 18


MARKET_NAME = {
    '3otc': 'OTC.TW',
    '2tse': 'TSE.TW',
}

FUTURES_NAME = {
    '1fitx': 'FITX',
    '1fitxn': 'FITXN',
}


class market():
    def input(self, name):
        pyautogui.click(1500, 70)
        pyautogui.write(name)
        time.sleep(1)
        pyautogui.click(1500, 110)
        time.sleep(0.5)

    def K(self, name, dir, prevDay):
        self.moveK(prevDay)
        self.screenshotImage(dir, f'{name}-1')

    def trend(self, name, dir):
        pyautogui.click(200, 130)
        time.sleep(0.5)
        self.calendar()
        time.sleep(0.5)
        self.screenshotImage(dir, f'{name}-2')

    def screenshotImage(self, dir, name):
        pyautogui.screenshot(os.path.join(dir, f'{name}.png'), region=(72, 112, 3750, 1860))

    def moveK(self, prevDay):
        pyautogui.click(500, 130)
        time.sleep(0.5)
        pyautogui.click(1140, 1950, prevDay)
        time.sleep(0.05 * prevDay)

    def calendar(self):
        pass

    def screenshot(self, output, prevDay=0):
        for n, c in MARKET_NAME.items():
            self.input(c)
            self.trend(n, output)
            self.K(n, output, prevDay)

        for n, c in FUTURES_NAME.items():
            self.input(c)
            self.trend(n, output)

    def run(self, dir):
        pass

    def start(self, dir):
        self.run(dir)
        pyautogui.alert(text='完成', title='結果')


class marketNow(market):
    def run(self, output):
        self.screenshot(output)


class marketHistory(market):
    def __init__(self, date, dir):
        self.prevDay, self.prevMonth, self.dayX, self.dayY = calendarXY(date, dir)

    def run(self, output):
        self.screenshot(output, prevDay=self.prevDay)

    def moveToK(self):
        self.moveK(self.prevDay)

    def calendar(self):
        pyautogui.click(90, 220)
        pyautogui.click(100, 260, self.prevMonth)
        time.sleep(0.5)
        pyautogui.click(42 + (53 * self.dayX), 306 + (29 * self.dayY))
