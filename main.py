# -*- coding: utf-8 -*-

import json
import os
import tkinter as tk
import frame


class app(tk.Tk):
    def __init__(self):
        super(app, self).__init__()
        self.currentPath = os.path.dirname(os.path.abspath(__file__))
        self.configs = self.readConfig()
        self.title('股票')

    def readConfig(self):
        config = os.path.join(self.currentPath, 'config.json')

        if os.path.exists(config):
            return json.load(open(config, encoding='utf-8'))

        return {
            'data': '',
            'json': '',
            'tick': '',
            'output': '',
            'code': '',
            'open': '',
        }

    def menu(self):
        m = tk.Menu(self)
        fileMenu = tk.Menu(m, tearoff=0)
        fileMenu.add_command(label='資料', command=lambda: self.runDate())
        fileMenu.add_command(label='圖', command=lambda: self.runImage())
        fileMenu.add_command(label='看盤', command=lambda: self.runWatch())

        m.add_cascade(label="功能", menu=fileMenu)
        self.config(menu=m)

    def run(self, ui):
        for f in self.winfo_children():
            f.destroy()

        self.menu()
        ui()
        self.mainloop()

    def runDate(self):
        self.run(lambda: frame.main(self, config=self.configs, path=self.currentPath))

    def runImage(self):
        self.run(lambda: frame.image(self, config=self.configs))

    def runWatch(self):
        self.run(lambda: frame.Watch(self, config=self.configs))


app().runWatch()
