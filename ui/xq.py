import tkinter as tk
import calendar
from stock import data
from datetime import datetime
from . import ui
from xq import image as xq


class stockImage(ui.process):
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
class stockImageDay(stockImage):
    def __init__(self, master, w, h):
        stockImage.__init__(self, master, w, h)

    def run(self):
        xq.day().start(self.total.get(), self.output.get())


# xq 自動擷取歷史走勢與技術分析圖參數
class stockImageHistory(stockImage):
    def __init__(self, master, w, h):
        stockImage.__init__(self, master, w, h)

        self.date = tk.StringVar()
        self.dir = tk.StringVar()
        self.date.set(datetime.now().date())

        tk.Label(master, text='日期:', font=ui.FONT).place(x=10, y=self.ey * 2)
        tk.Entry(master, textvariable=self.date, font=ui.FONT).place(x=self.ex, y=self.ey * 2)

        tk.Label(master, text='檔案:', font=ui.FONT).place(x=10, y=self.ey * 3)
        tk.Entry(master, textvariable=self.dir, font=ui.FONT).place(x=self.ex, y=self.ey * 3)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda:
            self.dir.set(ui.openDir())
        ).place(x=self.w * 50, y=self.h * 28)

    def run(self):
        date = datetime.fromisoformat(self.date.get())
        nM = datetime.now().month
        nY = datetime.now().year

        prevDay = data.stock(self.dir.get()).afterDates(self.date.get()).__len__()
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

        for index in range(weeks.__len__()):
            if date.day in weeks[index]:
                dayY = index + 1

        xq.history(prevDay=prevDay, prevMonth=prevMonth, dayX=dayX, dayY=dayY).start(
            self.total.get(),
            self.output.get()
        )


# xq 大盤圖參數
class marketImage(ui.process):
    def __init__(self, master, w, h):
        ui.process.__init__(self, master, w, h)

        self.output = tk.StringVar()

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.output.set(ui.openDir())
        ).place(x=self.w * 50, y=self.h * 8)

        self.addRunBtn(master)

    def run(self):
        pass
