# -*- coding: utf-8 -*-

import os
import tkinter as tk
from ui import ui
from xlsx import stock


class stockInfo(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        if config != None:
            self.output.set(config['json'])

        tk.Label(master, text='檔案:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇xlsx',
            font=ui.BTN_FONT,
            command=lambda: self.input.set(ui.openFile().name)
        ).place(x=w * 50, y=10)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.output.set(ui.openDir())
        ).place(x=w * 50, y=h * 8)

        self.addRunBtn(master)

    def run(self):
        stock.info(self.input.get()).output(self.output.get())
        self.showSuccess()


def csv_path(config):
    return os.path.join(config['data'], 'csv')


def stock_csv_path(config):
    return os.path.join(csv_path(config), 'stock')


def trend_csv_path(config):
    return os.path.join(csv_path(config), 'trend')


def tick_csv_path(config):
    return os.path.join(csv_path(config), 'tick')


def stock_trend_csv_path(config):
    return os.path.join(trend_csv_path(config), 'stock')


def fund_csv_path(config):
    return os.path.join(csv_path(config), 'fund')
