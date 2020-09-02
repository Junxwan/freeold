from stock import data
from xlsx import cmoney
import pandas as pd
import numpy as np


# p1 = pd.read_csv('/private/var/www/other/free/csv/202008.csv', index_col=[0, 1], header=[0])
# p2 = pd.read_csv('/private/var/www/other/free/csv/202007.csv', index_col=[0, 1], header=[0])
#
# p2.columns = np.arange(p1.columns.__len__(), p1.columns.__len__() + p2.columns.__len__())
#
# pd.merge(p1, p2, on=['code', 'name'], how='inner')

#
# for c in list(set([v[0] for v in p.index.values])):
#     p.loc[c].loc['open']
#
# # w.loc['open'][w.loc['open'] > -0.5]
# arrays = [np.array(['1101', '1101', '1102', '1102']),
#           np.array(['open', 'close', 'open', 'close'])]
# df = pd.DataFrame(np.random.randn(4, 4), index=arrays)
#
# leftindex = pd.MultiIndex.from_product([['1101', '1102'], ['open', 'close']],
#                                        names=['code', 'name'])
# left = pd.DataFrame({'0': [100 * i for i in range(1, 5)]}, index=leftindex)
#
# rightindex = pd.MultiIndex.from_product([['1101', '1102'], ['open', 'close']],
#                                         names=['code', 'name'])
# right = pd.DataFrame({'0': [10 * i for i in range(1, 5)]}, index=rightindex)
#
# right.columns = np.arange(left.columns.__len__(), left.columns.__len__() + right.columns.__len__())
#
# w = pd.merge(left, right, on=['code', 'name'], how='inner')
# w.to_csv('/private/var/www/other/free/1.csv')
# left.join(right, on=['code', 'name'], how='inner')

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
def t(c, v):
    pass


d = data.stocks('/private/var/www/other/free/csv')
d.year('2020')

# d.date('2020-08-13')

d.month('202006')
# d.read('202008')
# d.read('202007')
# d.read('202006')
# d.year('2015')
# d.date('2015-03-04', t)

# cmoney.year('/private/var/www/other/free/year').output('/private/var/www/other/free/csv')

pass
