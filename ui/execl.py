import os
import tkinter as tk
import openpyxl
from . import ui, other
from auto import xq as xq
from stock import data
from xlsx import xq as execl, csv


class toData(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        if config != None:
            self.output.set(os.path.join(config['data'], 'csv', 'stock'))

        self.default_output()

        tk.Label(master, text='xlsx:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text=self.openInputText(),
            font=ui.BTN_FONT,
            command=self.openInput
        ).place(x=self.w * 50, y=10)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=self.openOutPut
        ).place(x=self.w * 50, y=self.h * 8)

        self.addRunBtn(master)

    def default_output(self):
        pass

    def openInputText(self):
        return ""

    def openInput(self):
        pass

    def openOutPut(self):
        pass


class ToCsv(toData):
    def openInputText(self):
        return '選擇檔案'

    def openInput(self):
        self.input.set(ui.openDir())

    def openOutPut(self):
        self.output.set(ui.openDir())

    def run(self):
        csv.ToCsv(self.input.get(), self.output.get())
        self.showSuccess()
