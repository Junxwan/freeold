import os
import time
import logging
import requests
import glob
import tkinter as tk
import pandas as pd
from datetime import datetime
from crawler import twse
from . import ui, other
from xlsx import twse as xtwse


# 月營收
class MonthRevenue(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.output = tk.StringVar()
        self.year = tk.IntVar()
        self.month = tk.IntVar()

        self.year.set(datetime.now().year)
        self.month.set(datetime.now().month)

        tk.Label(master, text='年:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.year, font=ui.FONT).place(x=self.ex, y=10)

        tk.Label(master, text='月:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.month, font=ui.FONT).place(x=self.ex, y=self.ey)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey * 2)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey * 2)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.output.set(ui.openDir())
        ).place(x=w * 50, y=h * 18)

        self.addRunBtn(master)

    def run(self):
        m = "%02d" % self.month.get()

        dir = os.path.join(self.output.get(), str(self.year.get()))

        if os.path.exists(dir) == False:
            os.mkdir(dir)

        logging.info(f"read {self.year.get()}-{m}")

        data = twse.month_revenue(self.year.get(), self.month.get())
        data.to_csv(os.path.join(dir, f"{self.year.get()}-{m}.csv"), index=False, encoding='utf_8_sig')

        logging.info(f"save {self.year.get()}-{m}")

        self.showSuccess()


# 財報
class FinancialReport(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.output = tk.StringVar()
        self.year = tk.IntVar()
        self.season = tk.IntVar()

        self.year.set(datetime.now().year)

        tk.Label(master, text='年:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.year, font=ui.FONT).place(x=self.ex, y=10)

        tk.Label(master, text='季:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.season, font=ui.FONT).place(x=self.ex, y=self.ey)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey * 2)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey * 2)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.output.set(ui.openDir())
        ).place(x=w * 50, y=h * 18)

        self.addRunBtn(master)

    def run(self):
        while (True):
            try:
                self._run()
                break

            except requests.exceptions.ConnectionError as e:
                logging.error(e.__str__())
                logging.info("等待重新執行")

                for i in range(10):
                    time.sleep(1)

            except Exception as e:
                logging.error(e.__str__())
                break

        self.showSuccess()

    def _run(self):
        if self.season.get() == 0:
            seasons = [4, 3, 2, 1]
        else:
            seasons = [self.season.get()]

        for season in seasons:
            logging.info(f"read {self.year.get()} Q{season} ...")
            for code in twse.season_codes(self.year.get(), season):
                self._get(code, self.year.get(), season)

    def _get(self, code, year, season):
        outPath = os.path.join(self.output.get(), self.dir_name())

        if os.path.exists(os.path.join(outPath, f"{year}Q{season}", f"{code}.csv")):
            return

        d = self.get(code, year, season)

        if len(d) == 0:
            logging.info(f"{code} not found")
        else:
            for k, v in d.items():
                dir = os.path.join(outPath, k)
                f = os.path.join(dir, f"{code}.csv")

                if os.path.exists(f):
                    continue

                if os.path.exists(dir) == False:
                    os.mkdir(dir)

                v.to_csv(f, index=False, encoding='utf_8_sig')

                logging.info(f"save {code} {k}")

        time.sleep(6)

    def get(self, code, year, season):
        return {}

    def dir_name(self):
        return ""


# 資產負債表
class BalanceSheet(FinancialReport):
    def get(self, code, year, season):
        return twse.balance_sheet(code, year, season)

    def dir_name(self):
        return "balance_sheet"


# 綜合損益表
class ConsolidatedIncomeStatement(FinancialReport):
    def get(self, code, year, season):
        return twse.consolidated_income_statement(code, year, season)

    def dir_name(self):
        return "consolidated_income_statement"


# 現金流量表
class CashFlowStatement(FinancialReport):
    def get(self, code, year, season):
        return twse.cash_flow_statement(code, year, season)

    def dir_name(self):
        return "cash_flow_statement"


# 權益變動表
class ChangesInEquity(FinancialReport):
    def get(self, code, year, season):
        return twse.changes_in_equity(code, year, season)

    def dir_name(self):
        return "changes_in_equity"


# 股利
class Dividend(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.output = tk.StringVar()
        self.year = tk.IntVar()

        self.year.set(datetime.now().year)

        tk.Label(master, text='年:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.year, font=ui.FONT).place(x=self.ex, y=10)

        tk.Label(master, text='輸出:', font=ui.FONT).place(x=10, y=self.ey)
        tk.Entry(master, textvariable=self.output, font=ui.FONT).place(x=self.ex, y=self.ey)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.output.set(ui.openDir())
        ).place(x=w * 50, y=h * 18)

        self.addRunBtn(master)

    def run(self):
        outPath = os.path.join(self.output.get(), "dividend")
        data = twse.dividend(self.year.get())
        data.to_csv(os.path.join(outPath, f"{self.year.get()}.csv"), index=False, encoding='utf_8_sig')
        logging.info(f"save {self.year.get()}")
        self.showSuccess()


# 合併資產負債表
class MergeBalanceSheet(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='輸入:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.input.set(ui.openDir())
        ).place(x=w * 50, y=5)

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
        logging.info("合併 資產負債表...")

        xtwse.balance_sheet(self.input.get(), self.output.get())

        logging.info("資產負債表 合併完成")

        self.showSuccess()


# 合併綜合損益表
class MergeConsolidatedIncomeStatement(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='輸入:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.input.set(ui.openDir())
        ).place(x=w * 50, y=5)

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
        logging.info("合併 綜合損益表...")

        xtwse.consolidated_income_statement(self.input.get(), self.output.get())

        logging.info("綜合損益表 合併完成")

        self.showSuccess()


# 合併現金流量表
class MergeCashFlowStatement(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='輸入:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.input.set(ui.openDir())
        ).place(x=w * 50, y=5)

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
        logging.info("合併 現金流量表...")

        xtwse.cash_flow_statement(self.input.get(), self.output.get())

        logging.info("現金流量表 合併完成")

        self.showSuccess()


# 合併權益變動表
class MergeChangesInEquity(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='輸入:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.input.set(ui.openDir())
        ).place(x=w * 50, y=5)

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
        logging.info("合併 權益變動表...")

        xtwse.changes_inEquity(self.input.get(), self.output.get())

        logging.info("權益變動表 合併完成")

        self.showSuccess()


# 合併月收盤價
class MergeMonthClosePrice(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='輸入:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.input.set(ui.openDir())
        ).place(x=w * 50, y=5)

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
        logging.info("合併 月價格...")

        xtwse.month_close_price(self.input.get(), self.output.get())

        logging.info("月價格 合併完成")

        self.showSuccess()


# 合併股利
class MergeDividend(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='輸入:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.input.set(ui.openDir())
        ).place(x=w * 50, y=5)

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
        logging.info("合併 股利...")

        xtwse.dividend(self.input.get(), self.output.get())

        logging.info("股利 合併完成")

        self.showSuccess()


# 合併月營收
class MergeMonthRevenue(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='輸入:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.input.set(ui.openDir())
        ).place(x=w * 50, y=5)

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
        logging.info("合併 月營收...")

        xtwse.month_revenue(self.input.get(), self.output.get())

        logging.info("月營收 合併完成")

        self.showSuccess()


# 合併財報
class MergeFinancial(ui.process):
    def __init__(self, root, master, w, h, config=None):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

        tk.Label(master, text='輸入:', font=ui.FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.input, font=ui.FONT).place(x=self.ex, y=10)
        tk.Button(
            master,
            text='選擇目錄',
            font=ui.BTN_FONT,
            command=lambda: self.input.set(ui.openDir())
        ).place(x=w * 50, y=5)

        self.addRunBtn(master)

    def run(self):
        logging.info("合併 財報...")

        data = {}
        f = os.path.join(self.input.get(), "財報.xlsx")

        for p in glob.glob(os.path.join(self.input.get(), "*.csv")):
            name = os.path.basename(p).split('.')[0]
            logging.info(f"read {name}...")

            data[name] = pd.read_csv(p)

        with pd.ExcelWriter(f) as writer:
            for k, v in data.items():
                logging.info(f"save {k}...")
                v.to_excel(writer, sheet_name=k, index=False)

        logging.info("開始合併財報")
        writer.close()
        logging.info("合併財報完成")

        self.showSuccess()

# 一鍵合併財報
class MergeFinancials(MergeFinancial):
    def run(self):
        logging.info("合併 資產負債表...")
        xtwse.balance_sheet(os.path.join(self.input.get(), 'balance_sheet'), self.input.get())
        logging.info("資產負債表 合併完成")

        logging.info("合併 綜合損益表...")
        xtwse.consolidated_income_statement(os.path.join(self.input.get(), 'consolidated_income_statement'),
                                            self.input.get())
        logging.info("綜合損益表 合併完成")

        logging.info("合併 現金流量表...")
        xtwse.cash_flow_statement(os.path.join(self.input.get(), 'cash_flow_statement'), self.input.get())
        logging.info("現金流量表 合併完成")

        logging.info("合併 權益變動表...")
        xtwse.changes_inEquity(os.path.join(self.input.get(), 'changes_in_equity'), self.input.get())
        logging.info("權益變動表 合併完成")

        logging.info("合併 月營收...")
        xtwse.month_revenue(os.path.join(self.input.get(), 'month_revenue'), self.input.get())
        logging.info("月營收 合併完成")

        logging.info("合併 股利...")
        xtwse.dividend(os.path.join(self.input.get(), 'dividend'), self.input.get())
        logging.info("股利 合併完成")

        MergeFinancial.run(self)
