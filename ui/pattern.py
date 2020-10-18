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


class Select():
    def __init__(self, config):
        self.k = data.K(other.stock_csv_path(config))

    def run(self, d1, d2, y, date=None, similarity=1) -> pd.DataFrame:
        result = []
        y = pd.Series(y).dropna()
        stock = self.k.get_stock()
        data = stock.query(date, False)
        dates = data.loc[2330].loc[name.DATE]
        di = dates.index[0]
        ys = dict()

        for i in range((d2 + 1) - d1):
            ys[d1 + i] = self.y(y, d1 + i)

        logging.info(f"ys: {ys.__str__()}")

        for code in data.index.levels[0].tolist():
            ma = data.loc[code].loc[name.CLOSE].iloc[::-1].rolling(2).mean().round(2).iloc[::-1][:d2]
            s = dict()

            for i in range((d2 + 1) - d1):
                i = d1 + i
                v = np.corrcoef(ma[:i].iloc[::-1].tolist(), ys[i])[0][1]

                if v >= similarity:
                    s[i] = v

            if len(s) > 0:
                p = pd.Series(s)
                i = p.idxmax()
                result.append([
                    code,
                    stock.info(code)['name'],
                    dates[di + i - 1],
                    date,
                    round(p.max(), 4),
                    ys[i].tolist(),
                    ma[:i].iloc[::-1].tolist()
                ])

            logging.info(f"{code} - {date}")

        logging.info(f"total: {len(result)}")

        return pd.DataFrame(
            result, columns=['code', 'name', 'start_date', 'end_date', 'similarity', 'ys', 'ma']
        ).sort_values(by='similarity', ascending=False)

    def y(self, y, l):
        new_indices = np.linspace(0, len(y) - 1, l)
        spl = UnivariateSpline(np.arange(0, len(y)), y, k=3, s=0)
        return np.around(spl(new_indices).tolist(), decimals=2)


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
