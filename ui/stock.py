# -*- coding: utf-8 -*-

import os
import tkinter as tk
from datetime import datetime
from . import ui, other
from stock import data, builder as sql


class select(ui.process):
    stock = None

    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.startDate = tk.StringVar()
        self.endDate = tk.StringVar()
        self.dir = tk.StringVar()
        self.output = tk.StringVar()

        self.startDate.set(datetime.now().date())

        if config != None:
            self.dir.set(other.stock_csv_path(config))

        tk.Label(master, text='開始日期:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.startDate, font=ui.FONT).place(x=self.ex, y=10)

        tk.Label(master, text='結束日期:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.endDate, font=ui.FONT).place(x=self.ex, y=self.ey)

        tk.Label(master, text='檔案:', font=ui.FONT).place(x=10, y=self.ey * 2)
        tk.Entry(master, textvariable=self.dir, font=ui.FONT).place(x=self.ex, y=self.ey * 2)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda:
            self.dir.set(ui.openDir())
        ).place(x=self.w * 50, y=self.h * 18)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey * 3)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey * 3)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda:
            self.output.set(ui.openDir())
        ).place(x=self.w * 50, y=self.h * 28)

        self.addRunBtn(master)

    def run(self):
        query = sql.query().read(
            os.path.join(
                self.output.get(),
                os.path.basename(self.output.get())
            ) + '.json'
        )
        if self.stock == None:
            self.stock = data.Stock(self.dir.get())

        self.stock.run(query, self.startDate.get(), end=self.endDate.get(), output=self.output.get())
        self.showSuccess()
