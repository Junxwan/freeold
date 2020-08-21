import tkinter as tk
from datetime import datetime

from . import ui
from stock import weak


# 每日弱勢股
class weakDay(ui.process):
    def __init__(self, master):
        self.date = tk.StringVar()
        self.dir = tk.StringVar()
        self.output = tk.StringVar()

        self.date.set(datetime.now().date())

        tk.Label(master, text='日期:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.date, font=ui.FONT).place(x=130, y=10)

        tk.Label(master, text='檔案:', font=ui.FONT).place(x=10, y=50)
        tk.Entry(master, textvariable=self.dir, font=ui.FONT).place(x=130, y=50)
        tk.Button(master, text='選擇目錄', font=ui.FONT, command=lambda: self.dir.set(ui.openDir())).place(x=350,
                                                                                                       y=50)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=90)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=130, y=90)
        tk.Button(master, text='選擇目錄', font=ui.FONT, command=lambda: self.output.set(ui.openDir())).place(x=350, y=90)

        self.addRunBtn(master)

    def run(self):
        weak.run(self.date.get(), self.dir.get(), self.output.get())
        self.showSuccess()
