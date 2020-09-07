# -- coding: utf-8 --

import glob
import os
import time
import tkinter as tk
import openpyxl
import pyautogui
import mplfinance as mpf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticks
from stock import data
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui import cmoney, xq, stock, log, other, ui
from PIL import Image, ImageTk
from mplfinance._styledata import charles


class main():
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
        btn = tk.Button(self.btnGroupFrame, text='日轉json', command=lambda: self.switchArg(cmoney.dayToData))
        btn.place(x=5, y=5)

        btn = tk.Button(self.btnGroupFrame, text='年轉json', command=lambda: self.switchArg(cmoney.yearToData))
        btn.place(x=5, y=self.h * 6)

        btn = tk.Button(self.btnGroupFrame, text='個股轉json', command=lambda: self.switchArg(cmoney.stockToData))
        btn.place(x=5, y=self.h * 12)

        self.setLog('cmoney')

    # 選股功能按鈕組
    def stockButtonGroup(self):
        btn = tk.Button(self.btnGroupFrame, text='選股', command=lambda: self.switchArg(stock.select))
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


class watch():
    def __init__(self, root, config=None):
        self.root = root
        self.size = pyautogui.size()
        self.width = self.size.width
        self.height = self.size.height
        self.config = config
        self.root.geometry(f'{self.width}x{self.height}')

        labelFontSize = 15
        tickLabelStyle = {'fontsize': labelFontSize, 'rotation': 0}

        self.mainLayout()

        s = data.stock('/private/var/www/other/free/csv')
        # s.read('202009')
        s.read('202008')
        s.read('202007')
        s.read('202006')
        s.read('202005')
        s.read('202004')
        s.read('202003')
        s.read('202002')
        s.read('202001')
        # s.read('2019')
        # s.read('2018')

        code = 2330

        e = pd.DataFrame([
            s.data.loc[code][i].tolist() for i in s.data.loc[code]],
            columns=s.data.loc[code].index.tolist()
        )
        e['date'] = pd.to_datetime(e['date'])
        e = e.set_index('date').sort_index()
        i = 0
        li = e.shape[0] - (60 + i)
        ri = e.shape[0] + i
        self.datas = e[li:ri]

        candle = {
            'up': '#9A0000',
            'down': '#FFFFFF'
        }

        style = charles.style

        # 蠟燭顏色
        style['marketcolors']['candle'] = candle
        style['marketcolors']['edge'] = {
            'up': '#FF0000',
            'down': '#FFFFFF'
        }
        style['marketcolors']['wick'] = candle
        style['marketcolors']['ohlc'] = candle
        style['marketcolors']['volume'] = {
            'up': '#9A0000',
            'down': '#23B100'
        }

        # 格子線
        style['gridstyle'] = '-'

        # 格子內顏色
        style['facecolor'] = '#0f0f10'
        style['base_mpl_style'] = 'dark_background'

        fig, axs = mpf.plot(
            self.datas,
            type='candle',
            style=style,
            datetime_format='%Y-%m-%d',
            ylabel='',
            ylabel_lower='',
            figsize=(self.width / 100, self.height / 100),
            update_width_config={
                'volume_width': 0.85
            },
            scale_padding={
                'left': 0.6,
                'right': 0.55,
                'bottom': 0.3,
            },
            volume=True,
            returnfig=True,
            panel_ratios=(4, 1)
        )

        close = e['close']
        xdates = np.arange(self.datas.shape[0])

        xMax = self.datas.index.get_loc(self.datas['high'].idxmax())
        yMax = self.datas['high'].max()
        if int(yMax) == yMax:
            yMax = int(yMax)

        xMin = self.datas.index.get_loc(self.datas['low'].idxmin())
        yMin = self.datas['low'].min()
        if int(yMin) == yMin:
            yMin = int(yMin)

        priceLoc = PriceLocator(yMax, yMin)
        dateFom = DateFormatter()
        dateLoc = DateLocator(self.datas.index)

        axs[0].xaxis.set_major_locator(dateLoc)
        axs[0].xaxis.set_major_formatter(dateFom)
        axs[0].yaxis.set_major_locator(priceLoc)
        axs[0].yaxis.set_major_formatter(PriceFormatter())

        volumeF = lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (
                x * 1e-3) if x >= 1e3 else '%1.0f' % x

        axs[2].yaxis.set_major_locator(VolumeLocator(self.datas['volume']))
        axs[2].yaxis.set_major_formatter(mticks.FuncFormatter(volumeF))

        xOffset = {
            1: 1.35,
            2: 1.35,
            3: 1.35,
            4: 1.05,
            5: 1.35,
            6: 1.35,
            7: 1.45,
        }

        axs[0].annotate(
            yMax,
            xy=(xMax, yMax),
            xytext=(xMax - xOffset[len(str(yMax))], yMax + priceLoc.tick / 2),
            color='white',
            size=labelFontSize,
            arrowprops=dict(arrowstyle="simple")
        )
        axs[0].annotate(
            yMin,
            xy=(xMin, yMin),
            xytext=(xMin - xOffset[len(str(yMin))], yMin - priceLoc.tick / 1.5),
            color='white',
            size=labelFontSize,
            arrowprops=dict(arrowstyle="simple")
        )

        ma5 = close.rolling(5).mean().round(2).values[li:ri]
        ma10 = close.rolling(10).mean().round(2).values[li:ri]
        ma20 = close.rolling(20).mean().round(2).values[li:ri]
        self.datas.loc[:, '5ma'] = ma5
        self.datas.loc[:, '10ma'] = ma10
        self.datas.loc[:, '20ma'] = ma20

        axs[0].plot(xdates, ma5, linewidth=1.8, color='#FF8000')
        axs[0].plot(xdates, ma10, linewidth=1.8, color='#00CCCC')
        axs[0].plot(xdates, ma20, linewidth=1.8, color='#00CC66')
        # ax1.plot(xdates, pd.Series(close).rolling(60).mean().values[li:ri], linewidth=1.8, color='#FFFF00')
        # ax1.plot(xdates, pd.Series(close).rolling(120).mean().values[li:ri], linewidth=1.8, color='#6600CC')
        # ax1.plot(xdates, pd.Series(close).rolling(240).mean().values[li:ri], linewidth=1.8, color='#CC00CC')

        yt = priceLoc.getTicks()

        axs[0].text(-11, yt[-1], 'd:', fontsize=16, color='white')
        axs[0].text(-11, yt[-1] - priceLoc.tick * 1.5, 'o:', fontsize=16, color='white')
        axs[0].text(-11, yt[-1] - priceLoc.tick * 3, 'c:', fontsize=16, color='white')
        axs[0].text(-11, yt[-1] - priceLoc.tick * 4.5, 'h:', fontsize=16, color='white')
        axs[0].text(-11, yt[-1] - priceLoc.tick * 6, 'l:', fontsize=16, color='white')
        axs[0].text(-11, yt[-1] - priceLoc.tick * 7.5, 'v:', fontsize=16, color='white')
        axs[0].text(-11, yt[-1] - priceLoc.tick * 9, '5m:', fontsize=15, color='#FF8000')
        axs[0].text(-11, yt[-1] - priceLoc.tick * 10.5, '10m:', fontsize=15, color='#00CCCC')
        axs[0].text(-11, yt[-1] - priceLoc.tick * 12, '20m:', fontsize=15, color='#00CC66')
        # ax1.text(9, topLx, 'SMA60', fontsize=30, color='#FFFF00')
        # ax1.text(13.5, topLx, 'SMA120', fontsize=30, color='#6600CC')
        # ax1.text(18.5, topLx, 'SMA240', fontsize=30, color='#CC00CC')

        for l in axs[0].get_yticklabels():
            l.update(tickLabelStyle)

        for l in axs[0].get_xticklabels():
            l.update(tickLabelStyle)

        for l in axs[2].get_yticklabels():
            l.update(tickLabelStyle)

        for l in axs[2].get_xticklabels():
            l.update(tickLabelStyle)

        # plt.show()

        self.canvas = FigureCanvasTkAgg(fig, self.watchFrame)
        self.event = MoveEvent(self.canvas, self.datas, yt=priceLoc.tick, yMax=yt[-1])

        self.canvas.draw()

        self.canvas.get_tk_widget().focus_force()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def mainLayout(self):
        self.topHeight = int(self.height * 0.8)

        self.topFrame = tk.Frame(self.root, width=self.width, height=self.topHeight, bg='grey')
        self.topFrame.pack(side=tk.TOP)
        self.topFrame.pack_propagate(0)

        self.bottomHeight = int(self.height * 0.2)

        self.bottomFrame = tk.Frame(self.root, width=self.width, height=self.bottomHeight, bg='black')
        self.bottomFrame.pack(side=tk.BOTTOM)
        self.bottomFrame.pack_propagate(0)

        self.watchLayout()

    def watchLayout(self):
        self.watchFrame = tk.Frame(self.topFrame, width=self.width * 0.9, height=self.topHeight)
        self.watchFrame.pack(side=tk.LEFT)
        self.watchFrame.pack_propagate(0)

        self.listFrame = tk.Frame(self.topFrame, width=self.width * 0.1, height=self.topHeight, bg='#C0C0C0')
        self.listFrame.pack(side=tk.LEFT)
        self.listFrame.pack_propagate(0)


class DateLocator(mticks.Locator):
    def __init__(self, data):
        self.data = data
        self.loc = None

    def __call__(self):
        if self.loc != None:
            return self.loc
        return self.tick_values(None, None)

    def getTicks(self):
        return self.__call__()

    def tick_values(self, vmin, vmax):
        monthFirstWorkDay = {}

        for i, d in enumerate(self.data):
            if d.month not in monthFirstWorkDay:
                monthFirstWorkDay[d.month] = i

        self.loc = list(monthFirstWorkDay.values())

        return self.loc


class PriceLocator(mticks.Locator):
    tickLevel = [50, 25, 10, 7.5, 5, 2.5, 1, 0.5, 0.25, 0.1, 0.05]

    def __init__(self, max, min):
        self.max = max
        self.min = min
        self.ticks = []

        diff = max - min
        self.tick = self.tickLevel[0]

        for i, t in enumerate(self.tickLevel):
            d = (diff / t)
            if d > 10:
                self.tick = t
                break

    def __call__(self):
        return self.tick_values(None, None)

    def getTicks(self):
        return self.tick_values(None, None)

    def tick_values(self, vmin, vmax):
        if len(self.ticks) > 0:
            return self.ticks

        start = self.min - (self.min % self.tick)

        for i in range(20):
            p = start + (self.tick * i)
            self.ticks.append(start + (self.tick * i))

            if p > self.max:
                self.ticks.insert(0, start - self.tick)
                self.ticks.append(p + self.tick)
                break

        self.axis.set_view_interval(self.ticks[0], self.ticks[-1])

        return np.asarray(self.ticks)


class VolumeLocator(mticks.Locator):
    def __init__(self, data):
        self.data = data

    def __call__(self):
        return self.tick_values(None, None)

    def tick_values(self, vmin, vmax):
        max = self.data.max()
        min = self.data.min()
        step = 10 ** (len(str(int((max - min) / 3))) - 1)
        diff = (max - min) / 3
        step = int((diff - diff % step) + step)

        return [step * i for i in range(5)]


class DateFormatter(mticks.Formatter):
    def __call__(self, x, pos=0):
        if x < 0:
            return ''
        return self.axis.major.locator.data[x].strftime('%Y-%m-%d')

    def getTicks(self):
        if len(self.locs) == 0:
            self.locs = self.axis.major.locator.loc

        return [self.__call__(x, 0) for x in self.locs]


class PriceFormatter(mticks.Formatter):
    def __call__(self, x, pos=None):
        if pos == 0:
            return ''

        return '%1.2f' % x


class MoveEvent(tk.Frame):
    def __init__(self, canvas, data, yt=0, yMax=0):
        tk.Frame.__init__(self)

        self._data = data
        self.canvas = canvas
        self._yMax = yMax
        self._yt = yt

        self.moveEvent = self.canvas.mpl_connect('motion_notify_event', self.move)
        self.clickEvent = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.releaseEvent = self.canvas.mpl_connect('button_release_event', self.on_release)

        self.ax = canvas.figure.axes[0]
        self.axv = canvas.figure.axes[2]

        self._xv = None
        self._xh = None
        self._yv = None

        self._style = dict(fontsize=18, color='white')
        self._isPress = False

        self.init_text()

    def draw(self, event):
        x = round(event.xdata)
        date = self._data.index[x]
        p = self._data.loc[date]
        date = date.strftime('%Y-%m-%d')

        if self._xv == None:
            self._xv = self.ax.axvline(x=x, color='#FFFF00', linewidth=0.5)
            self._xh = self.ax.axhline(y=(p['close']), color='#FFFF00', linewidth=0.5)
            self._yv = self.axv.axvline(x=x, color='#FFFF00', linewidth=0.5)
        else:
            self._xv.set_xdata(x)
            self._xh.set_ydata(p['close'])
            self._yv.set_xdata(x)

            self.set_text(date, p)

        self.canvas.draw_idle()

    def set_text(self, date, price):
        self._date.set_text(date)
        self._open.set_text(price['open'])
        self._close.set_text(price['close'])
        self._high.set_text(price['high'])
        self._low.set_text(price['low'])
        self._volume.set_text(price['volume'])
        self._5ma.set_text(price['5ma'])
        self._10ma.set_text(price['10ma'])
        self._20ma.set_text(price['20ma'])

    def init_text(self):
        date = self._data.index[-1]
        price = self._data.loc[date]

        self._date = self.ax.text(-9.5, self._yMax, date.strftime('%Y-%m-%d'), fontsize=13, color='white')
        self._open = self.ax.text(-9.5, self._yMax - self._yt * 1.5, price['open'], self._style)
        self._close = self.ax.text(-9.5, self._yMax - self._yt * 3, price['close'], self._style)
        self._high = self.ax.text(-9.5, self._yMax - self._yt * 4.5, price['high'], self._style)
        self._low = self.ax.text(-9.5, self._yMax - self._yt * 6, price['low'], self._style)
        self._volume = self.ax.text(-9.5, self._yMax - self._yt * 7.5, int(price['volume']), self._style)
        self._5ma = self.ax.text(-8.5, self._yMax - self._yt * 9, int(price['5ma']), self._style)
        self._10ma = self.ax.text(-8.5, self._yMax - self._yt * 10.5, int(price['10ma']), self._style)
        self._20ma = self.ax.text(-8.5, self._yMax - self._yt * 12, int(price['20ma']), self._style)

    def on_press(self, event):
        self._isPress = True
        self.draw(event)

    def on_release(self, event):
        self._isPress = False

    def move(self, event):
        if self._isPress:
            self.draw(event)
