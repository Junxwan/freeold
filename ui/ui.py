import threading
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk

FONT = ('Helvetica', 18, "bold")

SMALL_FONT = ('Helvetica', 13, "bold")


def openFile():
    return filedialog.askopenfile(
        filetypes=(("xlsx File", "*.xlsx"), ("All Files", "*.*")),
        title="Choose a file."
    )


def openDir():
    return filedialog.askdirectory(
        title="Choose a dir."
    )


class process():
    def addRunBtn(self, master):
        tk.Button(master, text='執行', font=FONT, command=self.start).place(x=500, y=250)

    def run(self):
        pass

    def start(self):
        t = threading.Thread(target=self.run)
        t.start()

    def showSuccess(self):
        messagebox.showinfo('結果', '完成')

    def showMessageBox(self, message, title='結果'):
        messagebox.showinfo(title, message)
