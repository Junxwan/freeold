import tkinter as tk
import logging
import os
from datetime import datetime


def init(dir, name, stream):
    dir = os.path.join(dir, 'log')

    if os.path.exists(dir) == False:
        os.mkdir(dir)

    filename = os.path.join(dir, datetime.now().strftime(f"%Y-%m-%d-{name}.log"))
    log = logging.getLogger()

    for hdlr in log.handlers[:]:
        log.removeHandler(hdlr)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=filename)

    log.addHandler(ui(stream))


class ui(logging.Handler):
    def __init__(self, stream):
        logging.Handler.__init__(self)
        self.stream = stream

    def emit(self, record):
        self.stream.insert(tk.END, f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {self.format(record)}')
        self.stream.see(tk.END)
