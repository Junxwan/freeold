import logging
import pandas as pd
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from stock import data, name
from ui import other
from scipy.interpolate import UnivariateSpline
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Watch():
    def __init__(self, frame, config=None):
        self._frame = frame
        self.config = config
        self.canvas = None

        self._fig, self._axes = plt.subplots()
        self._axes.grid(True)
        self._axes.set_xlim(0.0, 19.0)
        self._axes.set_ylim(0.0, 19.0)
        self._axes.xaxis.set_major_locator(ticker.MultipleLocator(1))
        self._axes.yaxis.set_major_locator(ticker.MultipleLocator(1))

        self._axes.tick_params(axis='y', labelsize=20)
        self._axes.tick_params(axis='x', labelsize=20)

        self._axes.set_facecolor('#CCE5FF')
        self._fig.patch.set_facecolor('#E0E0E0')

        self._canvas = FigureCanvasTkAgg(self._fig, self._frame)
        self._moveEvent = MoveEvent(self._canvas, self._axes)

    def set(self, y):
        self._moveEvent.clear()
        self._moveEvent.set_y(y)

    def data(self):
        return self._moveEvent.y()

    # 執行
    def pack(self):
        self._canvas.draw()
        self._canvas.get_tk_widget().focus_force()
        self._canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


class CorrLine():
    def __init__(self, frame):
        self._frame = frame
        self._fig = plt.figure()
        self._axes = None
        self._canvas = FigureCanvasTkAgg(self._fig, self._frame)

    def set(self, data1, data2):
        if self._axes is not None:
            self._axes[0].remove()
            self._axes[1].remove()

        self._axes = self._fig.subplots(1, 2)
        self._axes[0].grid(True)
        self._axes[1].grid(True)

        self._axes[0].plot(np.arange(len(data1)), data1)
        self._axes[1].plot(np.arange(len(data2)), data2)
        self._canvas.draw()

    # 執行
    def pack(self):
        self._canvas.draw()
        self._canvas.get_tk_widget().focus_force()
        self._canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

class MoveEvent(tk.Frame):
    def __init__(self, canvas, axes):
        tk.Frame.__init__(self)
        self.canvas = canvas
        self.axes = axes
        self._isPress = False
        self.o = None
        self.line = None
        self._x = [i for i in range(20)]
        self._y = {i: np.nan for i in range(20)}

        self.clickEvent = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.moveEvent = self.canvas.mpl_connect('motion_notify_event', self.move)
        self.releaseEvent = self.canvas.mpl_connect('button_release_event', self.on_release)

    def set_y(self, y):
        self._y = {i: y[i] for i in range(20)}
        self._draw()
        self.canvas.draw_idle()

    def y(self):
        return list(self._y.values())

    def draw(self, event):
        if event is None:
            return

        if event.xdata is None or event.ydata is None:
            return

        print(event.ydata)
        print(event.xdata)

        self._y[round(event.xdata)] = round(event.ydata, 1)

        self.clear()
        self._draw()

    def _draw(self):
        self.o = self.axes.plot(self._x, list(self._y.values()), 'o', linewidth=10, color='red')
        self.line = self.axes.plot(self._x, list(self._y.values()), linewidth=1, color='blue')

    def move(self, event):
        if self._isPress:
            self.draw(event)
            self.canvas.draw_idle()

    def on_press(self, event):
        if event.button == MouseButton.LEFT:
            self._isPress = True
            self.draw(event)
        elif event.button == MouseButton.RIGHT:
            self.clear()
            self._y = {i: np.nan for i in range(20)}

        self.canvas.draw_idle()

    def on_release(self, event):
        self._isPress = False

    def clear(self):
        if self.o is not None:
            self.o[0].remove()
            self.line[0].remove()

            self.o = None
            self.line = None
