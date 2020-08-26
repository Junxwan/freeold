import glob
import os
import tkinter as tk
import openpyxl
import pyautogui
from ui import cmoney, xq, stock, log, other, ui
from PIL import Image, ImageTk


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
        btn.place(x=self.w * 5, y=5)

        btn = tk.Button(self.btnFrame, text='cmoney', command=lambda: self.switchBtn(self.cmoneyButtonGroup))
        btn.place(x=self.w * 10, y=5)

        btn = tk.Button(self.btnFrame, text='個股', command=lambda: self.switchBtn(self.stockButtonGroup))
        btn.place(x=self.w * 18, y=5)

        btn = tk.Button(self.btnFrame, text='其他', command=lambda: self.switchBtn(self.otherButtonGroup))
        btn.place(x=5, y=self.h * 6)

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
        width = {
            1920: 77,
            3840: 100,
        }

        self.scrollbar = tk.Scrollbar(self.bottomFrame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(
            self.bottomFrame,
            bg='#eeeeee',
            yscrollcommand=self.scrollbar.set,
            width=width[self.size.width]
        )

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
        btn = tk.Button(self.btnGroupFrame, text='tick', command=lambda: self.switchArg(cmoney.stock))
        btn.place(x=5, y=5)

        btn = tk.Button(self.btnGroupFrame, text='市場', command=lambda: self.switchArg(cmoney.market))
        btn.place(x=5, y=self.h * 6)

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
    def __init__(self, root, config=None):
        self.root = root
        self.size = pyautogui.size()
        self.width = self.size.width
        self.height = self.size.height
        self.w = self.width / 100
        self.h = self.height / 100
        self.config = config
        self.stock = {}
        self.img = {}

        root.geometry(f'{self.width}x{self.height}')

        self.mainLayout()
        self.functionLayout()
        self.modelFrameLayout()
        self.buttnoGroupLayout()

    def mainLayout(self):
        self.topHeight = int(self.height * 0.75)

        self.viewFrame = tk.Frame(self.root, width=self.width, height=self.topHeight, bg='grey')
        self.viewFrame.pack(side=tk.TOP)
        self.viewFrame.pack_propagate(0)

        self.bottomHeight = int(self.height * 0.25)

        self.functionFrame = tk.Frame(self.root, width=self.width, height=self.bottomHeight, bg='black')
        self.functionFrame.pack(side=tk.BOTTOM)
        self.functionFrame.pack_propagate(0)

    def functionLayout(self):
        self.modelFrame = tk.Frame(self.functionFrame, width=int((self.width / 3) / 2), height=self.bottomHeight)
        self.modelFrame.pack(side=tk.LEFT, padx=5)
        self.modelFrame.pack_propagate(0)

        self.stockFrame = tk.Frame(self.functionFrame, width=int((self.width / 3) / 2), height=self.bottomHeight)
        self.stockFrame.pack(side=tk.LEFT, padx=5)
        self.stockFrame.pack_propagate(0)

        self.inputFrame = tk.Frame(self.functionFrame, width=int(self.width / 3), height=self.bottomHeight)
        self.inputFrame.pack(side=tk.LEFT, padx=5)
        self.inputFrame.pack_propagate(0)

        self.groupListFrame = tk.Frame(self.functionFrame, width=int((self.width / 3) * 0.4), height=self.bottomHeight)
        self.groupListFrame.pack(side=tk.LEFT, padx=5)
        self.groupListFrame.pack_propagate(0)

        self.groupScrollbar = tk.Scrollbar(self.groupListFrame)
        self.groupScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.groupListbox = tk.Listbox(
            self.groupListFrame,
            bg='#eeeeee',
            font=ui.BIG_FONT,
            selectbackground="orange",
            yscrollcommand=self.groupScrollbar.set
        )

        self.groupListbox.bind('<KeyRelease-Up>', self.groupListEvent)
        self.groupListbox.bind('<KeyRelease-Down>', self.groupListEvent)
        self.groupListbox.bind('<Button-1>', self.groupListEvent)
        self.groupListbox.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.groupScrollbar.config(command=self.groupListbox.yview)

        self.stockListFrame = tk.Frame(self.functionFrame, width=int((self.width / 3) * 0.6), height=self.bottomHeight)
        self.stockListFrame.pack(side=tk.LEFT, padx=5)
        self.stockListFrame.pack_propagate(0)

        self.stockScrollbar = tk.Scrollbar(self.stockListFrame)
        self.stockScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stockListbox = tk.Listbox(
            self.stockListFrame,
            bg='#eeeeee',
            font=ui.BIG_FONT,
            selectbackground="orange",
            yscrollcommand=self.stockScrollbar.set,
            width=50
        )

        self.stockListbox.bind('<KeyRelease-Up>', self.stockListEvent)
        self.stockListbox.bind('<KeyRelease-Down>', self.stockListEvent)
        self.stockListbox.bind('<Button-1>', self.stockListEvent)
        self.stockListbox.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.stockScrollbar.config(command=self.stockListbox.yview)

    def modelFrameLayout(self):
        self.kModel = tk.BooleanVar()
        self.trendModel = tk.BooleanVar()

        tk.Checkbutton(
            self.modelFrame,
            text='K',
            font=ui.FONT,
            var=self.kModel,
            command=lambda: self.setModel(ui.K, self.kModel.get())
        ).place(x=5, y=5)

        tk.Checkbutton(
            self.modelFrame,
            text='走勢',
            font=ui.FONT,
            var=self.trendModel,
            command=lambda: self.setModel(ui.TREND, self.trendModel.get())
        ).place(x=5, y=self.w * 2)

    def buttnoGroupLayout(self):
        self.path = tk.StringVar()
        self.dir = tk.StringVar()

        tk.Button(
            self.stockFrame,
            text='選擇目錄',
            font=ui.FONT,
            command=self.openGroupList
        ).place(x=5, y=5)

        tk.Label(self.stockFrame, textvariable=self.path, font=ui.FONT).place(x=5, y=self.w * 2)
        tk.Label(self.stockFrame, textvariable=self.dir, font=ui.FONT).place(x=5, y=self.w * 4)

    def openGroupList(self):
        self.groupListbox.delete(0, tk.END)

        path = ui.openDir()
        self.dir.set(os.path.split(path)[1])
        self.path.set(path)

        for f in os.listdir(path):
            f = os.path.splitext(f)

            if f[-1] == '.xlsx':
                self.groupListbox.insert(tk.END, f[0])

    def setModel(self, name, isDisplay):
        for w in self.viewFrame.winfo_children():
            w.destroy()

        if isDisplay:
            self.img[name] = ''
        elif name in self.img:
            del self.img[name]

        w = self.sizes()
        i = self.img.__len__() - 1

        for name in self.img:
            photo = ImageTk.PhotoImage(Image.new('RGB', w[i], color='grey'))
            self.img[name] = tk.Label(self.viewFrame, image=photo)
            self.img[name].image = photo

            if self.img.__len__() == 1:
                self.img[name].pack(padx=5, pady=5)
            else:
                self.img[name].pack(side=tk.LEFT, padx=5, pady=5)

        self.setCurCode()

    def groupListEvent(self, event):
        self.stockListbox.delete(0, tk.END)
        self.stock.clear()

        path = os.path.join(self.path.get(), str(self.groupListbox.get(tk.ACTIVE))) + '.xlsx'
        ws = openpyxl.load_workbook(path)
        sheet = ws.active

        for rows in sheet.iter_rows(2, 0, 0, sheet.max_column):
            self.stockListbox.insert(tk.END, f'{rows[0].value} - {rows[1].value}')

        imageDir = os.path.join(self.path.get(), 'image', self.groupListbox.get(tk.ACTIVE))

        for d in os.listdir(imageDir):
            for f in glob.glob(os.path.join(imageDir, d, '*.png')):
                code = os.path.basename(f).split('.')[0]

                if code in self.stock:
                    self.stock[code][d] = f
                else:
                    self.stock[code] = {
                        d: f,
                    }

    def stockListEvent(self, event):
        self.setCurCode()

    def setCurCode(self):
        name = self.stockListbox.get(tk.ACTIVE)
        self.setCode(name.split('-')[0].strip())

    def setCode(self, code):
        if code in self.stock:
            for name in self.img:
                img = ImageTk.PhotoImage(
                    Image.open(self.stock[code][name]).resize(
                        (self.img[name].image.width(), self.img[name].image.height())
                    )
                )

                self.img[name].configure(image=img)
                self.img[name].image = img

    def sizes(self):
        return [(int(self.width * 0.6), self.topHeight), (int(self.width / 2), self.topHeight)]
