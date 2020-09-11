import logging
import os
import time
import tkinter as tk
import openpyxl
from crawler import cmoney as crawler
from xlsx import cmoney as xlsx
from . import ui


class tick(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.ck = tk.StringVar()
        self.session = tk.StringVar()
        self.output = tk.StringVar()
        self.date = tk.StringVar()

        if config != None:
            self.output.set(os.path.join(config['tick'], 'stock'))
            self.date.set(config['open'])

        tk.Label(master, text='CK:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.ck, font=ui.FONT).place(x=self.ex, y=10)

        tk.Label(master, text='Session:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.session, font=ui.FONT).place(x=self.ex, y=self.ey)

        tk.Label(master, text='日期或檔案:', font=ui.FONT).place(x=10, y=self.ey * 2)
        tk.Entry(master, textvariable=self.date, font=ui.FONT).place(x=self.ex, y=self.ey * 2)
        tk.Button(
            master,
            text='選擇xlsx',
            font=ui.BTN_FONT,
            command=lambda: self.date.set(ui.openFile().name)
        ).place(x=w * 50, y=h * 18)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey * 3)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey * 3)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.output.set(ui.openDir())
        ).place(x=w * 50, y=h * 28)

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
            self.call(date)

        self.showSuccess()

    def call(self, date):
        pass


# 抓取tick
class stock(tick):
    def __init__(self, root, master, w, h, config=None):
        tick.__init__(self, root, master, w, h, config=config)

        self.code = tk.StringVar()
        self.crawler = None

        if config != None:
            self.code.set(config['code'])

        tk.Label(master, text='個股清單:', font=ui.FONT).place(x=10, y=self.ey * 4)
        tk.Entry(master, textvariable=self.code, font=ui.FONT).place(x=self.ex, y=self.ey * 4)
        tk.Button(
            master,
            text='選擇xlsx',
            font=ui.BTN_FONT,
            command=lambda: self.code.set(ui.openFile().name)
        ).place(x=w * 50, y=h * 38)

    def call(self, date):
        logging.info('======================= start ' + date + ' =======================')

        if self.crawler == None:
            self.crawler = crawler.stock(self.ck.get(), self.session.get(), self.code.get(), self.output.get())

        self.crawler.get(date)

        logging.info('======================= end ' + date + ' =======================')


class market(tick):
    def __init__(self, root, master, w, h, config=None):
        tick.__init__(self, root, master, w, h, config=config)

        self.crawler = None

    def call(self, date):
        if self.crawler == None:
            self.crawler = crawler.market(self.ck.get(), self.session.get(), self.output.get())

        self.crawler.get(date)


class toData(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        if config != None:
            self.output.set(os.path.join(config['data'], 'csv'))

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

    def openInputText(self):
        return ""

    def openInput(self):
        pass

    def openOutPut(self):
        pass


# 個股每日行情轉檔案
class dayToData(toData):
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


# 個股年度行情轉檔案
class yearToData(toData):
    def openInputText(self):
        return '選擇目錄'

    def openInput(self):
        self.input.set(ui.openDir())

    def openOutPut(self):
        self.output.set(ui.openDir())

    def run(self):
        now = time.time()
        xlsx.year(self.input.get()).output(self.output.get())
        self.showMessageBox(
            f'完成，時間:{str(int((time.time() - now) / 60))}分'
        )


# 個股基本資料轉檔案
class stockToData(toData):
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
