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
        self.codes = tk.StringVar()

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
        tk.Label(master, text='個股:', font=ui.FONT).place(x=10, y=self.ey * 4)
        tk.Entry(master, textvariable=self.codes, font=ui.FONT).place(x=self.ex, y=self.ey * 4)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda:
            self.codes.set(ui.openDir())
        ).place(x=self.w * 50, y=self.h * 38)

        self.addRunBtn(master)

    def run(self):
        if self.query == None:
            self.query = data.Query(self.dir.get())

        self.query.run(
            self.startDate.get(),
            self.output.get(),
            end=self.endDate.get(),
            codes=self.codes.get(),
        )

        self.showSuccess()
