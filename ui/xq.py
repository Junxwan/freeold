import tkinter as tk


# xq 自動擷取當日走勢與技術分析圖參數
class imageDay(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Page1 one", font=('Helvetica', 18, "bold")).pack()


# xq 自動擷取歷史走勢與技術分析圖參數
class historyDay(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Page2 one", font=('Helvetica', 18, "bold")).pack()
