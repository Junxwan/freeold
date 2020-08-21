import tkinter as tk
import calendar
from datetime import datetime
from . import ui
from xq import item as xq
from xq.imageDay import image as day
from xq.imageHistory import image as history


class image(ui.process):
    def __init__(self, master, w, h):
        ui.process.__init__(self, master, w, h)

        self.total = tk.IntVar()
        self.output = tk.StringVar()

        tk.Label(master, text='總數:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.total, font=ui.FONT).place(x=self.ex, y=10)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.output.set(ui.openDir())
        ).place(x=self.w * 50, y=self.h * 8)

        self.addRunBtn(master)


# xq 自動擷取當日走勢與技術分析圖參數
class imageDay(image):
    def __init__(self, master, w, h):
        image.__init__(self, master, w, h)

    def run(self):
        xq.run(self.total, self.output, day())
        self.showSuccess()


# xq 自動擷取歷史走勢與技術分析圖參數
class historyDay(image):
    def __init__(self, master, w, h):
        image.__init__(self, master, w, h)

        self.date = tk.StringVar()
        self.date.set(datetime.now().date())

        tk.Label(master, text='日期:', font=ui.FONT).place(x=10, y=self.ey * 2)
        tk.Entry(master, textvariable=self.date, font=ui.FONT).place(x=self.ex, y=self.ey * 2)

    def run(self):
        date = datetime.fromisoformat(self.date.get())
        nM = datetime.now().month
        nY = datetime.now().year

        prevDay = 0
        prevMonth = 0
        dayX = 1
        dayY = date.isocalendar()[1] % 6

        if nY != date.year:
            prevMonth += ((nY - date.year) * 12)

        if nM != date.month:
            prevMonth += abs(nM - date.month)

        if date.isocalendar()[2] != 7:
            dayX = date.isocalendar()[2] + 1

        weeks = calendar.Calendar(calendar.SUNDAY).monthdayscalendar(date.year, date.month)

        for index in range(6):
            if date.day in weeks[index]:
                dayY = index + 1

        xq.run(self.total, self.output, history(prevDay=prevDay, prevMonth=prevMonth, dayX=dayX, dayY=dayY))
        self.showSuccess()
