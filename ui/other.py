import tkinter as tk
from ui import ui
from xlsx import stock


class stockInfo(ui.process):
    def __init__(self, master, w, h):
        ui.process.__init__(self, master, w, h)

        self.input = tk.StringVar()
        self.output = tk.StringVar()

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