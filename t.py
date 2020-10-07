import pandas as pd
from stock import data, name

d = data.Stock('/private/var/www/other/free/csv/stock')
d.readAll()
c = pd.read_csv('/private/var/www/other/free/code.csv')
list = []

for i, row in c.iterrows():
    v = d.data.loc[row['code']]
    id = (v.loc[name.DATE] <= row[name.DATE]).idxmax()
    v = v[id + 1]

    l = row.tolist()
    l.append(v[name.INCREASE])
    list.append(l)

pd.DataFrame(list, columns=[name.DATE, 'code', name.INCREASE]).to_csv('/private/var/www/other/free/result.csv')

pass
