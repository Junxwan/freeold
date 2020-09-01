from stock import data
from xlsx import cmoney
import pandas as pd
import numpy as np

p = pd.read_csv('/private/var/www/other/free/1.csv', index_col=[0, 1], header=[0])
# w.loc['open'][w.loc['open'] > -0.5]
arrays = [np.array(['1101', '1101', '1102', '1102']),
          np.array(['open', 'close', 'open', 'close'])]
df = pd.DataFrame(np.random.randn(4, 4), index=arrays)
w = p.loc[1101]
# q = pd.DataFrame([[1, 2], [4, 5], [7, 8]],
#                  index=['cobra', 'viper', 'sidewinder'],
#                  columns=['max_speed', 'shield']).to_numpy().tolist()
#
# n = 10
# colors = np.random.choice(['1101', '1101', '1102', '1102'], size=n)
# foods = np.random.choice(['open', 'close', 'open', 'close'], size=n)
# index = pd.MultiIndex.from_arrays([colors, foods], names=['color', 'food'])
# r = pd.DataFrame(np.random.randn(n, 2), index=index)
#
#
# def t(c, v):
#     pass


# d = data.stocks('/private/var/www/other/free/json')
# d.year('2015')
# d.date('2015-03-04', t)

# cmoney.year('/private/var/www/other/free/year').output('/private/var/www/other/free/json')

pass
