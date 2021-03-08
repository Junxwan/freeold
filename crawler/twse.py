import requests
import time
import pandas as pd
import numpy as np
from io import StringIO

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'

HEADERS = {
    'User-Agent': USER_AGENT,
}


# 月營收
def month_revenue(year, month):
    t = [
        ['sii', 0],
        ['sii', 1],
        ['otc', 0],
        ['otc', 1],
    ]

    revenue = []
    year = year - 1911

    for n in t:
        r = requests.get(f"https://mops.twse.com.tw/nas/t21/{n[0]}/t21sc03_{year}_{month}_{n[1]}.html", headers=HEADERS)
        r.encoding = 'big5-hkscs'

        table = pd.read_html(StringIO(r.text), encoding='big5-hkscs')
        data = pd.concat([df for df in table if df.shape[1] == 11])
        revenue = revenue + data.iloc[:, :3].to_numpy().tolist()

        time.sleep(6)

    revenue = pd.DataFrame(revenue, columns=['code', 'name', 'value']).sort_values(by=['code'])
    return revenue[revenue['code'] != '合計']


# 資產負債表
def balance_sheet(code, year, season):
    data = {}
    year = year - 1911
    season = "%02d" % season

    st = {
        3: "Q1",
        6: "Q2",
        9: "Q3",
        12: "Q4",
    }

    ct = [
        [0, 1, 2],
        [0, 3, 4],
        [0, 5, 6],
        [0, 7, 8],
    ]

    r = requests.post("https://mops.twse.com.tw/mops/web/ajax_t164sb03", {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'TYPEK2': "",
        'keyword4': "",
        'code1': "",
        "checkbtn": "",
        "queryName": "co_id",
        "inpuType": "co_id",
        "TYPEK": "all",
        "isnew": "false",
        "co_id": code,
        'year': year,
        'season': season,
    }, headers=HEADERS)

    r.encoding = 'utf8'
    table = pd.read_html(r.text)

    if len(table) <= 1:
        return {}

    table = table[-1]
    columns = table.columns.tolist()[1:]

    for i in range(int(len(columns) / 2)):
        d = columns[i * 2][2]

        if len(d) != 10:
            break

        if d[4:6] == '01':
            continue

        data[f"{int(d[:3]) + 1911}{st[int(d[4:6])]}"] = pd.DataFrame(
            table.iloc[:, ct[i]].to_numpy().tolist(),
            columns=['項目', '金額', '%']
        )

    return data


# 綜合損益表
def consolidated_income_statement(code, year, season):
    data = {}
    year = year - 1911
    season = "%02d" % season

    ct = [
        [0, 1, 2],
        [0, 3, 4],
    ]

    r = requests.post("https://mops.twse.com.tw/mops/web/ajax_t164sb04", {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'TYPEK2': "",
        'keyword4': "",
        'code1': "",
        "checkbtn": "",
        "queryName": "co_id",
        "inpuType": "co_id",
        "TYPEK": "all",
        "isnew": "false",
        "co_id": code,
        'year': year,
        'season': season,
    }, headers=HEADERS)

    r.encoding = 'utf8'
    table = pd.read_html(r.text)

    if len(table) <= 1:
        return {}

    table = table[-1]
    columns = table.columns.tolist()[1:]

    for i in range(2):
        d = columns[i * 2][2]

        if len(d) == 21:
            if d[4:6] == '01' and d[15:17] == '03':
                s = "Q1"
            elif d[4:6] == '01' and d[15:17] == '06':
                s = "Q2"
            elif d[4:6] == '01' and d[15:17] == '09':
                s = "Q3"
            else:
                return {}
        elif len(d) == 7:
            s = f"Q{d[5:6]}"
        elif len(d) == 5:
            s = "Q4"
        elif d[3:] == '年上半年度':
            s = "Q2"
        elif d[3:] == '年度':
            s = "Q4"
        else:
            return {}

        data[f"{int(d[:3]) + 1911}{s}"] = pd.DataFrame(
            table.iloc[:, ct[i]].to_numpy().tolist(),
            columns=['項目', '金額', '%']
        )

    return data


# 現金流量表
def cash_flow_statement(code, year, season):
    data = {}
    year = year - 1911
    season = "%02d" % season

    r = requests.post("https://mops.twse.com.tw/mops/web/ajax_t164sb05", {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'TYPEK2': "",
        'keyword4': "",
        'code1': "",
        "checkbtn": "",
        "queryName": "co_id",
        "inpuType": "co_id",
        "TYPEK": "all",
        "isnew": "false",
        "co_id": code,
        'year': year,
        'season': season,
    }, headers=HEADERS)

    r.encoding = 'utf8'
    table = pd.read_html(r.text)

    if len(table) <= 1:
        return {}

    table = table[-1]
    columns = table.columns.tolist()[1:]

    for i in range(2):
        s = ''
        d = columns[i][2]

        if len(d) == 21:
            if d[4:6] == '01' and d[15:17] == '03':
                s = "Q1"
            if d[4:6] == '01' and d[15:17] == '06':
                s = "Q2"
            if d[4:6] == '01' and d[15:17] == '09':
                s = "Q3"
        elif len(d) == 7:
            s = f"Q{d[5:6]}"
        elif len(d) == 5:
            s = "Q4"
        else:
            return {}

        data[f"{int(d[:3]) + 1911}{s}"] = pd.DataFrame(
            table.iloc[:, [0, i + 1]].to_numpy().tolist(),
            columns=['項目', '金額']
        )

    return data


# 權益變動表
def changes_in_equity(code, year, season):
    data = {}
    year = year - 1911
    season = "%02d" % season

    r = requests.post("https://mops.twse.com.tw/mops/web/ajax_t164sb06", {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'TYPEK2': "",
        'keyword4': "",
        'code1': "",
        "checkbtn": "",
        "queryName": "co_id",
        "inpuType": "co_id",
        "TYPEK": "all",
        "isnew": "false",
        "co_id": code,
        'year': year,
        'season': season,
    }, headers=HEADERS)

    r.encoding = 'utf8'
    table = pd.read_html(r.text)

    if len(table) <= 1:
        return {}

    table = table[1:]

    for v in table:
        c = v.columns.tolist()[0][0]

        if c[5:] == '年度':
            s = "Q4"
        elif c[5:] == '年前3季':
            s = 'Q3'
        elif c[5:] == '年上半年度':
            s = 'Q2'
        elif c[5:] == '年第1季':
            s = 'Q1'
        else:
            return {}

        d = v.to_numpy().tolist()
        data[f"{int(c[2:5]) + 1911}{s}"] = pd.DataFrame(d[1:], columns=d[0])

    return data


# 已公布季報個股code
def season_codes(year, season):
    codes = []
    year = year - 1911

    for t in ['sii', 'otc']:
        r = requests.post("https://mops.twse.com.tw/mops/web/ajax_t163sb05", {
            'encodeURIComponent': 1,
            'step': 1,
            'firstin': 1,
            'off': 1,
            'TYPEK': t,
            'year': year,
            'season': season,
        }, headers=HEADERS)

        r.encoding = 'utf8'
        table = pd.read_html(r.text, header=None)
        codes = codes + pd.concat([df for df in table if df.shape[1] == 23 or df.shape[1] == 22])['公司代號'].tolist()

        time.sleep(5)

    return sorted(codes)
