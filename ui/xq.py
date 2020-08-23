import tkinter as tk
from . import ui
from xq import image as xq


class stockImage(ui.process):
    def __init__(self, root, master, w, h):
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
    def __init__(self, root, master, w, h):
        stockImage.__init__(self, root, master, w, h)

    def run(self):
        xq.stockNow().start(self.total.get(), self.output.get())


# xq 自動擷取歷史走勢與技術分析圖參數
class stockImageHistory(stockImage):
    def __init__(self, root, master, w, h):
        stockImage.__init__(self, root, master, w, h)

        self.date = tk.StringVar()
        self.dir = tk.StringVar()

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
        xq.stockHistory(self.date.get(), self.dir.get()).start(
            self.total.get(),
            self.output.get()
        )


# xq 大盤圖參數
class marketImage(ui.process):
    def __init__(self, root, master, w, h):
        ui.process.__init__(self, master, w, h)

        self.output = tk.StringVar()

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.output.set(ui.openDir())
        ).place(x=self.w * 50, y=10)

        self.addRunBtn(master)

    def run(self):
        xq.marketNow().start(self.output.get())


# xq 歷史大盤圖參數
class marketImageHistory(ui.process):
    def __init__(self, root, master, w, h):
        ui.process.__init__(self, master, w, h)

        self.dir = tk.StringVar()
        self.date = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='日期:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.date, font=ui.FONT).place(x=self.ex, y=10)

        tk.Label(master, text='檔案:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.dir, font=ui.FONT).place(x=self.ex, y=self.ey)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda:
            self.dir.set(ui.openDir())
        ).place(x=self.w * 50, y=self.h * 8)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey * 2)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey * 2)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.output.set(ui.openDir())
        ).place(x=self.w * 50, y=self.h * 18)

        self.addRunBtn(master)

    def run(self):
        xq.marketHistory(self.date.get(), self.dir.get()).start(self.output.get())


class move(ui.process):
    def __init__(self, root, master, w, h):
        ui.process.__init__(self, master, w, h)

        self.dir = tk.StringVar()
        self.date = tk.StringVar()
        self.allDate = tk.StringVar()
        self.historyTrendDate = tk.StringVar()
        self.historyKDate = tk.StringVar()

        tk.Label(master, text='檔案:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.dir, font=ui.FONT).place(x=self.ex * 1.5, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda:
            self.dir.set(ui.openDir())
        ).place(x=self.w * 55, y=10)

        tk.Label(master, text='日期:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.date, font=ui.FONT).place(x=self.ex * 1.5, y=self.ey)

        tk.Button(
            master,
            text='個籌',
            font=ui.BTN_FONT,
            command=lambda: self.all()
        ).place(x=10, y=self.h * 18)

        tk.Button(
            master,
            text='走勢',
            font=ui.BTN_FONT,
            command=lambda: self.historyTrend()
        ).place(x=self.ex * 0.5, y=self.h * 18)

        tk.Button(
            master,
            text='技術分析',
            font=ui.BTN_FONT,
            command=lambda: self.historyK()
        ).place(x=self.ex, y=self.h * 18)

        self.keyEvent(root)

    def all(self, event=None):
        xq.marketHistory(self.date.get(), self.dir.get()).moveToK()

    def historyTrend(self, event=None):
        xq.stockHistory(self.date.get(), self.dir.get()).moveTrend()

    def historyK(self, event=None):
        xq.stockHistory(self.date.get(), self.dir.get()).moveK()

    def keyEvent(self, master):
        master.focus_set()
        master.bind("<F1>", self.all)
        master.bind("<F2>", self.historyTrend)
        master.bind("<F3>", self.historyK)
