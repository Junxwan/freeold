import math

from stock import data, builder
from xlsx import cmoney
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf

# C:\\Users\\hugh8\\Desktop\\research\\data\\weak

# builder.query(). \
#     whereOpen('>', 10). \
#     whereVolume('>=', 1000). \
#     whereAmplitude('>=', 3). \
#     whereIncrease('<', 0). \
#     whereOpen('<', data.CLOSE). \
#     sortBy(data.AMPLITUDE). \
#     limit(100).setName('弱勢股').toJson('C:\\Users\\hugh8\\Desktop\\research\\data\\weak')

# data.stock('C:\\Users\\hugh8\\Desktop\\research\\data\\csv')

# cmoney.year('/private/var/www/other/free/year').output('/private/var/www/other/free/csv')


import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from PIL import Image, ImageTk


class ExampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.x = self.y = 0
        self.canvas = tk.Canvas(self, width=512, height=512, cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None

        self.start_x = None
        self.start_y = None

        self._draw_image()

    def _draw_image(self):
        self.canvas.create_image(0, 0, anchor="nw")

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y

        # create rectangle if not yet exist
        # if not self.rect:
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, fill="black")

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        pass


from matplotlib.backend_bases import MouseButton

# if __name__ == "__main__":
# app = ExampleApp()
# app.mainloop()

def Show(y):
    # 参数为一个list

    len_y = len(y)
    x = range(len_y)
    _y = [y[-1]] * len_y

    fig = plt.figure(figsize=(960 / 72, 360 / 72))
    ax1 = fig.add_subplot(1, 1, 1)

    ax1.plot(x, y, color='blue')
    line_x = ax1.plot(x, _y, color='skyblue')[0]
    line_y = ax1.axvline(x=len_y - 1, color='skyblue')

    ax1.set_title('aaa')
    # 标签
    text0 = plt.text(len_y - 1, y[-1], str(y[-1]), fontsize=10)

    def scroll(event):
        axtemp = event.inaxes
        x_min, x_max = axtemp.get_xlim()
        fanwei_x = (x_max - x_min) / 10
        if event.button == 'up':
            axtemp.set(xlim=(x_min + fanwei_x, x_max - fanwei_x))
        elif event.button == 'down':
            axtemp.set(xlim=(x_min - fanwei_x, x_max + fanwei_x))
        fig.canvas.draw_idle()
        # 这个函数实时更新图片的显示内容

    def motion(event):
        try:
            temp = y[int(np.round(event.xdata))]
            for i in range(len_y):
                _y[i] = temp
            line_x.set_ydata(_y)
            line_y.set_xdata(event.xdata)
            text0.set_position((event.xdata, temp))
            text0.set_text(str(temp))

            fig.canvas.draw_idle()  # 绘图动作实时反映在图像上
        except:
            pass

    fig.canvas.mpl_connect('scroll_event', scroll)
    fig.canvas.mpl_connect('motion_notify_event', motion)

    plt.show()


Show([1,2,3,4,5,6,7,8])

pass
