import codecs
import json
import os

from . import data


class query():
    def __init__(self):
        self.bindings = []
        self.sort = ''
        self.asc = False
        self.num = 0
        self.name = '選股'

    def setName(self, name):
        self.name = name
        return self

    def whereOpen(self, operator='=', value=0, **kwargs):
        return self.where(data.OPEN, operator, value, **kwargs)

    def whereClose(self, operator='=', value=0, **kwargs):
        return self.where(data.CLOSE, operator, value, **kwargs)

    def whereHigh(self, operator='=', value=0, **kwargs):
        return self.where(data.HIGH, operator, value, **kwargs)

    def whereLow(self, operator='=', value=0, **kwargs):
        return self.where(data.LOW, operator, value, **kwargs)

    def whereIncrease(self, operator='=', value=0, **kwargs):
        return self.where(data.INCREASE, operator, value, **kwargs)

    def whereAmplitude(self, operator='=', value=0, **kwargs):
        return self.where(data.AMPLITUDE, operator, value, **kwargs)

    def whereVolume(self, operator='=', value=0, **kwargs):
        return self.where(data.VOLUME, operator, value, **kwargs)

    def andWhere(self, k1, operator1, value1, k2, operator2, value2, index=0, num=0):
        b1 = bindings(k1, operator1, value1, index, num)
        b2 = bindings(k2, operator2, value2, index, num)
        b1.addBindings(b2, 'and')
        self.bindings.append(b1)
        return self

    def where(self, key, operator, value, index=0, num=0):
        self.bindings.append(bindings(key, operator, value, index, num))
        return self

    def sortBy(self, key):
        if type(key) != list:
            key = [key]

        self.sort = key
        return self

    def orderByAsc(self):
        self.asc = True
        return self

    def orderByDesc(self):
        self.asc = False
        return self

    def limit(self, num):
        self.num = num
        return self

    def read(self, file):
        f = codecs.open(file, 'r', 'utf-8')
        data = json.load(f)

        self.name = data['name']
        self.asc = data['asc']
        self.sort = data['sort']
        self.num = data['num']

        for b in data['bindings']:
            bind = bindings()
            [bind.setBind(**v) for v in b['bind']]
            bind.boolean = b['boolean']

            self.bindings.append(bind)

        return self

    def toJson(self, output):
        f = codecs.open(os.path.join(output, self.name) + '.json', 'w+', 'utf-8')
        f.write(json.dumps(self.toDict(), ensure_ascii=False))
        f.close()

    def toDict(self):
        bindings = []

        for b in self.bindings:
            bindings.append(dict(
                boolean=b.boolean,
                bind=b.bind,
            ))

        d = dict(
            name=self.name,
            asc=self.asc,
            sort=self.sort,
            num=self.num,
            bindings=bindings,
        )
        return d

    def exec(self, data):
        for b in self.bindings:
            if b.exec(data) == False:
                return False
        return True


class bindings():
    operator = {
        '==': lambda x, y: x == y,
        '!=': lambda x, y: x != y,
        '<>': lambda x, y: x != y,
        '<': lambda x, y: x < y,
        '>': lambda x, y: x > y,
        '<=': lambda x, y: x <= y,
        '>=': lambda x, y: x >= y,
    }

    def __init__(self, key=None, operator='==', value=0, index=0, num=0):
        self.bind = []
        self.boolean = ''

        if key != None:
            self.setBind(
                key=key,
                operator=operator,
                value=value,
                index=index,
                num=num,
            )

    def addBindings(self, bindings, boolean='and'):
        self.boolean = boolean

        for b in bindings.getBind():
            self.setBind(**b)

    def setBind(self, **kwargs):
        self.bind.append(kwargs)

    def getBind(self):
        return self.bind

    def exec(self, data):
        for b in self.bind:
            v1 = data.loc[b['key']]

            if b['num'] > 0:
                v1 = float(v1.iloc[b['index']:b['num']])
            else:
                v1 = float(v1.iloc[b['index']])

            if type(b['value']) == str:
                v2 = data.loc[b['value']]
                if b['num'] > 0:
                    v2 = float(v2.iloc[b['index']:b['num']])
                else:
                    v2 = float(v2.iloc[b['index']])
            else:
                v2 = b['value']

            if self.operator[b['operator']](v1, v2) == False:
                return False
