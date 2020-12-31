# 統計弱勢股中昨日紅K，今天開高(10點前)走低(11點前)

import pandas as pd
import glob
import configparser
import os
from stock import name, data

NAME = 'weak_yesterday_red_trend_high_low'
config = configparser.ConfigParser()
config.read('../config.ini')
data_path = os.path.abspath(dict(config['path'])['data'])
weak_path = os.path.join(data_path, 'csv', 'strategy', 'weak', 'yesterday_red_trend_high10_low11')
stock = data.Stock(os.path.join(data_path, 'csv', 'stock'))
stock.readAll()
dates = stock.dates()
result = []
