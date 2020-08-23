import json
import os
import tkinter as tk
import pyautogui
from ui import cmoney, xq, stock, log, other


class data():
    def __init__(self, root, config=None, path=None):
        self.root = root
        self.config = config
        self.size = pyautogui.size()
        self.width = int(self.size.width / 2)
        self.height = int(self.size.height / 2)
        self.w = self.width / 100
        self.h = self.height / 100
        self.isTop = False
        self.currentPath = path

        root.geometry(f'{self.width}x{self.height}')
        self.mainLayout()
        self.frameLayout()

    # 主layout
    def mainLayout(self):
        self.topHeight = int(self.height * 0.6)

        self.topFrame = tk.Frame(self.root, width=self.width, height=self.topHeight)
        self.topFrame.pack(side=tk.TOP, padx=5)
        self.topFrame.pack_propagate(0)

        self.bottomHeight = int(self.height * 0.4)

        self.bottomFrame = tk.Frame(self.root, width=self.width, height=self.bottomHeight)
        self.bottomFrame.pack(side=tk.BOTTOM, padx=5)
        self.bottomFrame.pack_propagate(0)

    # ui layout
    def frameLayout(self):
        self.buttonLayout()
        self.argLayout()
        self.logLayout()
        self.resultLayout()

    # 按鈕 layout
    def buttonLayout(self):
        self.btnFrame = tk.LabelFrame(self.topFrame, text='功能', width=int(self.width * 0.25), height=self.topHeight)
        self.btnFrame.pack(side=tk.LEFT)
        self.btnFrame.pack_propagate(0)

        btn = tk.Button(self.btnFrame, text='爬', command=lambda: self.switchBtn(self.dataButonGroup))
        btn.place(x=5, y=5)

        btn = tk.Button(self.btnFrame, text='xq', command=lambda: self.switchBtn(self.xqButtonGroup))
        btn.place(x=self.w * 3.5, y=5)

        btn = tk.Button(self.btnFrame, text='cmoney', command=lambda: self.switchBtn(self.cmoneyButtonGroup))
        btn.place(x=self.w * 6.5, y=5)

        btn = tk.Button(self.btnFrame, text='個股', command=lambda: self.switchBtn(self.stockButtonGroup))
        btn.place(x=self.w * 13.5, y=5)

        btn = tk.Button(self.btnFrame, text='其他', command=lambda: self.switchBtn(self.otherButtonGroup))
        btn.place(x=self.w * 17.5, y=5)

        self.btnGroupFrame = tk.Frame(self.btnFrame, width=int(self.width * 0.25), bg='#eeeeee',
                                      height=int(self.topHeight * 0.7))
        self.btnGroupFrame.pack(side=tk.BOTTOM)
        self.btnGroupFrame.pack_propagate(0)

    # 參數 layout
    def argLayout(self):
        self.argFrame = tk.LabelFrame(
            self.topFrame,
            text='參數',
            bg='#eeeeee',
            width=self.width - int(self.width * 0.25),
            height=self.topHeight
        )

        self.argFrame.pack(side=tk.RIGHT)
        self.argFrame.pack_propagate(0)

    # log layout
    def logLayout(self):
        self.scrollbar = tk.Scrollbar(self.bottomFrame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(self.bottomFrame, bg='#eeeeee', yscrollcommand=self.scrollbar.set,
                                  width=100)

        self.listbox.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.scrollbar.config(command=self.listbox.yview)

    # result layout
    def resultLayout(self):
        self.resultFrame = tk.Frame(self.bottomFrame, bg='#eeeeee', width=int(self.width * 0.25),
                                    height=self.bottomHeight)
        self.resultFrame.pack(side=tk.LEFT, pady=2)
        self.resultFrame.pack_propagate(0)

        btn = tk.Button(self.resultFrame, text='置頂', command=lambda: self.setWinTop())
        btn.place(x=5, y=5)

    # 抓取資料功能按鈕組群
    def dataButonGroup(self):
        btn = tk.Button(self.btnGroupFrame, text='tick', command=lambda: self.switchArg(cmoney.tick))
        btn.place(x=5, y=5)

        self.setLog('data')

    # xq功能按鈕組群
    def xqButtonGroup(self):
        btn = tk.Button(self.btnGroupFrame, text='當日走勢與技術分析截圖', command=lambda: self.switchArg(xq.stockImageDay))
        btn.place(x=5, y=5)

        btn = tk.Button(self.btnGroupFrame, text='歷史走勢與技術分析截圖', command=lambda: self.switchArg(xq.stockImageHistory))
        btn.place(x=5, y=self.h * 6)

        btn = tk.Button(self.btnGroupFrame, text='大盤截圖', command=lambda: self.switchArg(xq.marketImage))
        btn.place(x=5, y=self.h * 12)

        btn = tk.Button(self.btnGroupFrame, text='歷史大盤截圖', command=lambda: self.switchArg(xq.marketImageHistory))
        btn.place(x=5, y=self.h * 18)

        btn = tk.Button(self.btnGroupFrame, text='定位', command=lambda: self.switchArg(xq.move))
        btn.place(x=5, y=self.h * 24)

        self.setLog('xq')

    # cmoney功能按鈕組群
    def cmoneyButtonGroup(self):
        btn = tk.Button(self.btnGroupFrame, text='日轉json', command=lambda: self.switchArg(cmoney.dayToJson))
        btn.place(x=5, y=5)

        btn = tk.Button(self.btnGroupFrame, text='年轉json', command=lambda: self.switchArg(cmoney.yearToJson))
        btn.place(x=5, y=self.h * 6)

        btn = tk.Button(self.btnGroupFrame, text='個股轉json', command=lambda: self.switchArg(cmoney.stockToJson))
        btn.place(x=5, y=self.h * 12)

        self.setLog('cmoney')

    # 選股功能按鈕組
    def stockButtonGroup(self):
        btn = tk.Button(self.btnGroupFrame, text='每日弱勢股', command=lambda: self.switchArg(stock.weakDay))
        btn.place(x=5, y=5)

        self.setLog('stock')

    # 其他功能按鈕組群
    def otherButtonGroup(self):
        btn = tk.Button(self.btnGroupFrame, text='個股資料轉json', command=lambda: self.switchArg(other.stockInfo))
        btn.place(x=5, y=5)

        self.setLog('other')

    # 切換 按鈕群組 layout內容
    def switchBtn(self, pack):
        self.listbox.delete(0, tk.END)

        for f in self.btnGroupFrame.winfo_children():
            f.destroy()

        pack()

        self.btnGroupFrame.pack()

    # 切換 參數 layout內容
    def switchArg(self, frame):
        self.listbox.delete(0, tk.END)

        for f in self.argFrame.winfo_children():
            f.destroy()

        frame(self.root, self.argFrame, self.w, self.h, self.config)

    # 視窗置頂
    def setWinTop(self):
        if self.isTop == False:
            self.isTop = True
        else:
            self.isTop = False

        self.root.wm_attributes('-topmost', self.isTop)

    def setLog(self, name):
        log.init(self.currentPath, name, self.listbox)


class image():
    def __init__(self, root):
        self.root = root
        self.size = pyautogui.size()
        self.width = int(self.size.width * 0.95)
        self.height = int(self.size.height * 0.8)

        root.geometry(f'{self.width}x{self.height}')

        self.mainLayout()

    def mainLayout(self):
        self.leftHeight = int(self.height * 0.75)

        self.leftFrame = tk.Frame(self.root, width=self.width, height=self.leftHeight, bg='grey')
        self.leftFrame.pack(side=tk.TOP, padx=5)
        self.leftFrame.pack_propagate(0)

        self.rightHeight = int(self.height * 0.25)

        self.rightFrame = tk.Frame(self.root, width=self.width, height=self.rightHeight, bg='black')
        self.rightFrame.pack(side=tk.BOTTOM, padx=5)
        self.rightFrame.pack_propagate(0)


class app(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.currentPath = os.path.dirname(os.path.abspath(__file__))
        self.configs = self.readConfig()
        self.title('股票')

    def readConfig(self):
        config = os.path.join(self.currentPath, 'config.json')

        if os.path.exists(config):
            return json.load(open(config, encoding='utf-8'))

        return {
            'data': '',
            'output': '',
            'code': '',
            'tick': '',
            'open': '',
            'weak': '',
        }

    def menu(self):
        m = tk.Menu(self)
        fileMenu = tk.Menu(m, tearoff=0)
        fileMenu.add_command(label='資料', command=lambda: self.runDate())
        fileMenu.add_command(label='圖', command=lambda: self.runImage())

        m.add_cascade(label="看盤", menu=fileMenu)
        self.config(menu=m)

    def run(self, ui):
        for f in self.winfo_children():
            f.destroy()

        self.menu()
        ui()
        self.mainloop()

    def runDate(self):
        self.run(lambda: data(self, config=self.configs, path=self.currentPath))

    def runImage(self):
        self.run(lambda: image(self))


app().runImage()
