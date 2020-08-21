import os
import tkinter as tk
import openpyxl
from crawler import cmoney as crawler
from xlsx import cmoney as xlsx
from . import ui


# 抓取tick
class tick(ui.process):
    def __init__(self, master):
        self.ck = ''
        self.session = ''
        self.code = tk.StringVar()
        self.output = tk.StringVar()
        self.date = tk.StringVar()

        tk.Label(master, text='CK:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.ck, font=ui.FONT).place(x=130, y=10)

        tk.Label(master, text='Session:', font=ui.FONT).place(x=10, y=50)
        tk.Entry(master, textvariable=self.session, font=ui.FONT).place(x=130, y=50)

        tk.Label(master, text='日期或檔案:', font=ui.FONT).place(x=10, y=90)
        tk.Entry(master, textvariable=self.date, font=ui.FONT).place(x=130, y=90)
        tk.Button(master, text='選擇xlsx', font=ui.FONT, command=lambda: self.date.set(ui.openFile().name)).place(x=350,
                                                                                                                y=90)

        tk.Label(master, text='個股清單:', font=ui.FONT).place(x=10, y=130)
        tk.Entry(master, textvariable=self.code, font=ui.FONT).place(x=130, y=130)
        tk.Button(master, text='選擇xlsx', font=ui.FONT, command=lambda: self.code.set(ui.openFile().name)).place(x=350,
                                                                                                                y=130)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=170)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=130, y=170)
        tk.Button(master, text='選擇目錄', font=ui.FONT, command=lambda: self.output.set(ui.openDir())).place(x=350, y=170)

        self.addRunBtn(master)

    def run(self):
        dates = []
        date = self.date.get()
        if os.path.isfile(self.date.get()):
            xlsx = openpyxl.load_workbook(date)
            for cell in xlsx.active:
                if cell[0].value == None:
                    continue

                dates.append(str(cell[0].value)[:10])
        else:
            dates.append(date)

        for date in dates:
            crawler.pullTick(date, self.ck, self.session, self.code, self.output)

        self.showSuccess()


class toJson(ui.process):
    def __init__(self, master):
        self.input = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='xlsx:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, width=35, font=ui.FONT).place(x=100, y=10)
        tk.Button(master, text=self.openInputText(), font=ui.FONT, command=self.openInput).place(
            x=470, y=10)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=50)
        tk.Entry(master, textvariable=self.output, width=35, font=ui.FONT).place(x=100, y=50)
        tk.Button(master, text='選擇目錄', font=ui.FONT, command=self.openOutPut).place(x=470, y=50)

        self.addRunBtn(master)

    def openInputText(self):
        return ""

    def openInput(self):
        pass

    def openOutPut(self):
        pass


# 個股每日行情轉json參數
class dayToJson(toJson):
    def openInputText(self):
        return '選擇檔案'

    def openInput(self):
        f = ui.openFile()
        if f != None:
            self.input.set(f.name)

    def openOutPut(self):
        self.output.set(ui.openDir())

    def run(self):
        xlsx.day(self.input.get()).output(self.output.get())
        self.showSuccess()


# 個股年度行情轉json參數
class yearToJson(toJson):
    def openInputText(self):
        return '選擇目錄'

    def openInput(self):
        self.input.set(ui.openDir())

    def openOutPut(self):
        self.output.set(ui.openDir())

    def run(self):
        self.showMessageBox(f"total {xlsx.year(self.input.get()).output(self.output.get())}")


# 個股基本資料轉json參數
class stockToJson(toJson):
    def openInputText(self):
        return '選擇檔案'

    def openInput(self):
        f = ui.openFile()
        if f != None:
            self.input.set(f.name)

    def openOutPut(self):
        self.output.set(ui.openDir())

    def run(self):
        xlsx.stock(self.input.get()).output(self.output.get())
        self.showSuccess()
