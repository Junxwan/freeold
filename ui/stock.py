import tkinter as tk
from datetime import datetime

from . import ui
from stock import weak


# 每日弱勢股
class weakDay(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.date = tk.StringVar()
        self.dir = tk.StringVar()
        self.output = tk.StringVar()

        self.date.set(datetime.now().date())

        if config != None:
            self.dir.set(config['data'])
            self.output.set(config['weak'])

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
            command=lambda:
            self.output.set(ui.openDir())
        ).place(x=self.w * 50, y=self.h * 18)

        self.addRunBtn(master)

    def run(self):
        weak.run(self.date.get(), self.dir.get(), self.output.get())
        self.showSuccess()
