# -*- coding: utf-8 -*-

import os
import tkinter as tk
import pandas as pd
from datetime import datetime
from . import ui, other, pattern
from stock import data


class select(ui.process):
    query = None

    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.startDate = tk.StringVar()
        self.endDate = tk.StringVar()
        self.dir = tk.StringVar()
        self.output = tk.StringVar()

        self.startDate.set(datetime.now().date())

        if config != None:
            self.dir.set(other.csv_path(config))

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
        if self.query == None:
            self.query = data.Query(self.dir.get())

        self.query.run(
            os.path.basename(self.output.get()),
            self.startDate.get(),
            end=self.endDate.get(),
            output=self.output.get()
        )

        self.showSuccess()


class Pattern(ui.process):
    query = None

    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.config = config
        self.date = tk.StringVar()
        self.start_range = tk.IntVar()
        self.end_range = tk.IntVar()
        self.similarity = tk.DoubleVar()
        self.output = tk.StringVar()
        self.select = None

        self.start_range.set(5)
        self.end_range.set(10)
        self.similarity.set(0.85)

        tk.Label(master, text='日期:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.date, font=ui.FONT).place(x=self.ex, y=10)

        tk.Label(master, text='比對範圍:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.start_range, width=5, font=ui.FONT).place(x=self.ex, y=self.ey)
        tk.Entry(master, textvariable=self.end_range, width=5, font=ui.FONT).place(x=self.ex * 1.6, y=self.ey)

        tk.Label(master, text='相似度:', font=ui.FONT).place(x=self.ex * 2.1, y=self.ey)
        tk.Entry(master, textvariable=self.similarity, width=5, font=ui.FONT).place(x=self.ex * 2.8, y=self.ey)

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
        if self.select == None:
            self.select = pattern.Select(self.config)

        stock = self.select.k.get_stock()

        if self.query == None:
            self.query = data.Query(other.csv_path(self.config), stock=stock)

        stocks = self.select.run(
            self.start_range.get(),
            self.end_range.get(),
            pd.read_csv(os.path.join(self.output.get(), 'pattern') + '.csv').iloc[0][1:].tolist(),
            date=self.date.get(),
            similarity=self.similarity.get(),
        )

        self.query.run(
            os.path.basename(self.output.get()),
            stocks['start_date'].min(),
            output=self.output.get(),
            end=self.date.get(),
            pattern=stocks,
        )

        self.showSuccess()
