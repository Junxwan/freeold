import tkinter as tk
from tkinter import filedialog

FONT = ('Helvetica', 18, "bold")


def openFile():
    return filedialog.askopenfile(
        filetypes=(("xlsx File", "*.xlsx"), ("All Files", "*.*")),
        title="Choose a file."
    )


def openDir():
    return filedialog.askdirectory(
        title="Choose a dir."
    )


# 抓取tick
class tick():
    def __init__(self, master):
        self.ck = ''
        self.session = ''
        self.date = ''
        self.code = tk.StringVar()

        tk.Label(master, text='CK:', font=FONT).place(x=10, y=10)
        tk.Entry(master, textvariable=self.ck, font=FONT).place(x=200, y=10)

        tk.Label(master, text='Session:', font=FONT).place(x=10, y=50)
        tk.Entry(master, textvariable=self.session, font=FONT).place(x=200, y=50)

        tk.Label(master, text='Date or xlsx Path:', font=FONT).place(x=10, y=90)
        tk.Entry(master, textvariable=self.date, font=FONT).place(x=200, y=90)

        tk.Label(master, text='Code Path:', font=FONT).place(x=10, y=130)
        tk.Button(master, text='選擇xlsx', font=FONT, command=self.openFile).place(x=200, y=130)
        tk.Label(master, text='1', textvariable=self.code, font=FONT).place(x=300, y=130)

        tk.Label(master, text='OutPut Path:', font=FONT).place(x=10, y=170)
        tk.Button(master, text='選擇輸出', font=FONT, command=self.openDir).place(x=200, y=170)

        tk.Button(master, text='執行', font=FONT, command=self.run).place(x=500, y=250)

    def openFile(self):
        self.code = openFile()
        print(self.code.name)

    def openDir(self):
        self.output = openDir()

    def run(self):
        pass


# 個股每日行情轉json參數
class dayToJson(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Page 2one", font=FONT).pack()


# 個股年度行情轉json參數
class yearToJson(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Page 3one", font=FONT).pack()


# 個股基本資料轉json參數
class stockToJson(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Page 3one", font=FONT).pack()
