import os
import glob
import pandas as pd
import numpy as np


# 營收
def month_revenue(path, toPath):
    d = {}
    m = []
    data = []

    for p in glob.glob(os.path.join(path, "*", "*.csv")):
        n = os.path.basename(p).split(".")[0]

        if int(f"{n[:4]}{n[5:]}") not in m:
            m.append(int(f"{n[:4]}{n[5:]}"))

        for i, v in pd.read_csv(p).iterrows():
            if v['code'] not in d:
                d[v['code']] = {}

            d[v['code']][int(f"{n[:4]}{n[5:]}")] = '{:,}'.format(v['value'])

    m.sort(reverse=True)

    for code in list(d.keys()):
        t = [code]

        for ym in m:
            if ym not in d[code]:
                t.append(0)
            else:
                t.append(d[code][ym])

        data.append(t)

    pd.DataFrame(data, columns=['code'] + m).to_csv(os.path.join(toPath, "月營收.csv"), encoding="utf_8_sig", index=False)


def merge(path, toPath, columns, name):
    data = {}

    seasons = []
    codes = []

    for p in glob.glob(os.path.join(path, "*", "*.csv")):
        tmp = {}
        code = os.path.basename(p).split('.')[0]
        season = os.path.dirname(p).split(os.path.sep)[-1]
        v = pd.read_csv(p)

        if code not in codes:
            codes.append(code)

        if season not in seasons:
            seasons.append(season)

        if code not in data:
            data[code] = {}

        if season not in data[code]:
            data[code][season] = []

        n = v['項目'].tolist()
        m = v['金額']

        for c in columns:
            if c not in n:
                tmp[c] = 0
            else:
                i = n.index(c)

                if np.isnan(m[i]):
                    i = i + n[i + 1:].index(c) + 1

                tmp[c] = '{:,}'.format(m[i])

        data[code][season] = tmp

    seasons.sort(reverse=True)
    codes.sort()

    index = pd.MultiIndex.from_product([codes, columns], names=['code', 'name'])

    csv = []
    for code in codes:
        for column in columns:
            v = []

            for season in seasons:
                if season not in data[code]:
                    v.append(0)
                else:
                    v.append(data[code][season][column])

            csv.append(v)

    pd.DataFrame(csv, index=index, columns=seasons).to_csv(os.path.join(toPath, f"{name}.csv"), encoding="utf_8_sig")


# 資產負債表
def balance_sheet(path, toPath):
    columns = [
        '現金及約當現金',
        '存貨',
        '應收票據淨額',
        '應收帳款淨額',
        '應收帳款－關係人淨額',
        '其他應收款淨額',
        '其他應收款－關係人淨額',
        '採用權益法之投資',
        '不動產、廠房及設備',
        '無形資產',
        '流動資產合計',
        '非流動資產合計',
        '資產總額',
        '短期借款',
        '應付短期票券',
        '應付帳款',
        '應付帳款－關係人',
        '其他應付款',
        '其他應付款項－關係人',
        '應付公司債',
        '遞延所得稅負債',
        '流動負債合計',
        '非流動負債合計',
        '負債總額',
        '股本合計',
        '歸屬於母公司業主之權益合計',
        '非控制權益',
        '權益總額',
        '負債及權益總計',
    ]

    merge(path, toPath, columns, '資產負債表')


# 綜合損益表
def consolidated_income_statement(path, toPath):
    columns = [
        '營業收入合計',
        '營業成本合計',
        '營業毛利（毛損）',
        '推銷費用',
        '管理費用',
        '研究發展費用',
        '營業費用合計',
        '營業利益（損失）',
        '營業外收入及支出合計',
        '稅前淨利（淨損）',
        '所得稅費用（利益）合計',
        '本期淨利（淨損）',
        '本期綜合損益總額',
        '母公司業主（淨利∕損）',
        '非控制權益（淨利∕損）',
        '母公司業主（綜合損益）',
        '非控制權益（綜合損益）',
        '基本每股盈餘',
    ]

    merge(path, toPath, columns, '綜合損益表')


# 現金流量表
def cash_flow_statement(path, toPath):
    columns = [
        '本期稅前淨利（淨損）',
        '折舊費用',
        '營業活動之淨現金流入（流出）',
        '取得不動產、廠房及設備',
        '投資活動之淨現金流入（流出）',
        '籌資活動之淨現金流入（流出）',
        '本期現金及約當現金增加（減少）數',
        '期初現金及約當現金餘額',
        '期末現金及約當現金餘額',
    ]

    merge(path, toPath, columns, '現金流量表')


# 權益變動表
def changes_inEquity(path, toPath):
    columns = [
        ['股本合計', '期初餘額'],
        ['股本合計', '期末餘額'],
        ['資本公積', '期初餘額'],
        ['資本公積', '期末餘額'],
        ['法定盈餘公積', '期初餘額'],
        ['法定盈餘公積', '期末餘額'],
        ['未分配盈餘（或待彌補虧損）', '期初餘額'],
        ['未分配盈餘（或待彌補虧損）', '期末餘額'],
        ['權益總額', '期初餘額'],
        ['權益總額', '期末餘額'],
    ]

    data = {}

    seasons = []
    codes = []

    for p in glob.glob(os.path.join(path, "*", "*.csv")):
        tmp = {}
        code = os.path.basename(p).split('.')[0]
        season = os.path.dirname(p).split(os.path.sep)[-1]
        v = pd.read_csv(p)

        if code not in codes:
            codes.append(code)

        if season not in seasons:
            seasons.append(season)

        if code not in data:
            data[code] = {}

        if season not in data[code]:
            data[code][season] = []

        item = v['會計項目'].tolist()
        c = v.columns.tolist()

        for k in columns:
            b = 0

            if k[0] in c and k[1] in item:
                b = '{:,}'.format(v[k[0]].tolist()[item.index(k[1])])

            tmp[f"{k[0]}-{k[1]}"] = b

        data[code][season] = tmp

    seasons.sort(reverse=True)
    codes.sort()
    columns = [f"{k[0]}-{k[1]}" for k in columns]

    index = pd.MultiIndex.from_product([codes, columns], names=['code', 'name'])

    csv = []
    for code in codes:
        for column in columns:
            v = []

            for season in seasons:
                if season not in data[code]:
                    v.append(0)
                else:
                    v.append(data[code][season][column])

            csv.append(v)

    pd.DataFrame(csv, index=index, columns=seasons).to_csv(os.path.join(toPath, "權益變動表.csv"), encoding="utf_8_sig")


# 月收盤價
def month_close_price(path, toPath):
    ps = {}

    for p in glob.glob(os.path.join(path, 'close', '*', '*.csv')):
        date = os.path.basename(p).split('.')[0]

        ym = int(f"{date[:4]}{date[5:7]}")

        if ym not in ps:
            ps[ym] = {}

        ps[ym][int(date[8:])] = p

    yms = list(ps.keys())
    yms.sort(reverse=True)

    data = []
    codes = []
    tmp = {}

    for ym in yms:
        if ym not in tmp:
            tmp[ym] = {}

        for i, v in pd.read_csv(ps[ym][list(ps[ym].keys())[-1]]).iterrows():
            if v['code'] not in codes:
                codes.append(int(v['code']))

            tmp[ym][int(v['code'])] = v['value']

    for code in codes:
        v = [code]

        for ym in yms:
            if code not in tmp[ym]:
                v.append(0)
            else:
                v.append(tmp[ym][code])

        data.append(v)

    pd.DataFrame(data, columns=['code'] + yms).to_csv(os.path.join(toPath, '月收盤價.csv'), index=False)
