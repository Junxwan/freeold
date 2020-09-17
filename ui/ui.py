# -*- coding: utf-8 -*-

import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

FONT = ('Helvetica', 18, "bold")

BTN_FONT = ('Helvetica', 15, "bold")

SMALL_FONT = ('Helvetica', 13, "bold")

BIG_FONT = ('Helvetica', 24, "bold")

K = 'k'

TREND = 'trend'


def openFile():
    return filedialog.askopenfile(
        filetypes=(("csv File", "*.csv"), ("xlsx File", "*.xlsx"), ("All Files", "*.*")),
        title="Choose a file."
    )


def openDir():
    return filedialog.askdirectory(
        title="Choose a dir."
    )


class process():
    def __init__(self, master, w, h):
        self.master = master
        self.w = w
        self.h = h
        self.ex = w * 15
        self.ey = h * 10

    def addRunBtn(self, master):
        tk.Button(master, text='執行', font=FONT, command=self.start).place(x=self.w * 65, y=self.h * 45)

    def run(self):
        pass

    def start(self):
        t = threading.Thread(target=self.run)
        t.start()

    def showSuccess(self):
        messagebox.showinfo('結果', '完成')

    def showMessageBox(self, message, title='結果'):
        messagebox.showinfo(title, message)
