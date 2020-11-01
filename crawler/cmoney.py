# -*- coding: utf-8 -*-
import glob
import json
import logging
import os
import time
import requests
import pandas as pd
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime
from stock import name
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'

HEADERS = {
    'User-Agent': USER_AGENT,
}


class Trend():
    def __init__(self, dir):
        self.dir = dir
        self.api = api()

    def get(self, date, code=None):
        pass

    def save(self, context, code, date, filePath):
        f = open(filePath, 'w+')
        f.write(json.dumps({
            'code': code,
            'date': date,
            'tick': context,
        }))
        f.close()

        return True


class stock(Trend):
    def read(self, path):
        return [c[0] for c in pd.read_csv(path, index_col=False, header=None).to_numpy().tolist()]

    def get(self, date, code=None):
        if (code == '') & (os.path.isdir(date)):
            for path in sorted(glob.glob(os.path.join(date, '*.csv')), reverse=True):
                if self._get(os.path.basename(path).split('.')[0], self.read(path)) == False:
                    return False

            return True
        elif (os.path.isfile(code)) & (os.path.isfile(date)):
            for date in self.read(date):
                if self._get(date, self.read(code)) == False:
                    return False

            return True
        elif (code == '') and (os.path.isfile(date)):
            return self._get(os.path.basename(date).split('.')[0], self.read(date))
        elif (os.path.isfile(code)) and (date != ''):
            return self._get(date, self.read(code))
        elif (code != '') & (date != ''):
            return self._get(date, [code])

        return False

    def _get(self, date, codes) -> bool:
        logging.info('======================= start ' + date + ' =======================')

        if len(codes) == 0:
            logging.info('無個股代碼')
            return False

        count = 0
        ok = 0
        failure = 0
        exists = 0
        emy = []

        t = str(date).replace('-', '')

        dir = os.path.join(self.dir, date[:4], date)

        if os.path.exists(dir) == False:
            os.makedirs(dir)

        for code in codes:
            filePath = os.path.join(dir, str(code)) + ".json"

            count += 1

            if os.path.exists(filePath):
                exists += 1
                logging.info(f'code: {code} date: {date} exists - {str(count)}')
                continue

            tData = self.api.trend(code, t)

            time.sleep(1.5)

            if tData == None:
                logging.info(f'code: {code} date: {date} empty - {str(count)}')
                emy.append(code)
                continue

            group = pd.DataFrame(tData).groupby(by='time')

            trend = []

            if group.groups[tData[0]['time']].size > 1:
                for index, value in group:
                    trend.append({
                        name.TIME: int(value[name.TIME].iloc[0]),
                        name.CLOSE: value[name.CLOSE].iloc[-1],
                        name.VOLUME: int(value[name.VOLUME].sum()),
                        name.HIGH: value[name.HIGH].iloc[-1],
                        name.LOW: value[name.LOW].iloc[-1],
                    })
            else:
                trend = tData

            date = datetime.fromtimestamp(tData[0]['time']).date().__str__()

            if self.save(trend, int(code), date, filePath):
                ok += 1
                logging.info(f'code: {code} date: {date} save trend - {str(count)}')
            else:
                failure += 1
                logging.info(f'code: {code} date: {date} save failure - {str(count)}')

        logging.info(
            f"total: {len(codes)} result: {ok + failure + exists + emy.__len__()} ok: {ok} failure: {failure} exists: {exists}"
        )
        logging.info(f"empty: {emy.__len__()} {emy.__str__()}")

        logging.info('======================= end ' + date + ' =======================')

        return True


class market(Trend):
    def __init__(self, dir):
        Trend.__init__(self, dir)

        tseDir = os.path.join(dir, 'tse')
        otcDir = os.path.join(dir, 'otc')
        self.code = {
            'TWA00': tseDir,
            'TWC00': otcDir,
        }

        for p in [tseDir, otcDir]:
            if os.path.exists(p) == False:
                os.makedirs(p)

    def get(self, date, code=None):
        t = str(date).replace('-', '')

        for code, dir in self.code.items():
            dir = os.path.join(dir, date[:4])

            if os.path.exists(dir) == False:
                os.mkdir(dir)

            filePath = os.path.join(dir, date) + '.json'

            if os.path.exists(filePath):
                logging.info(f'code: {code} date: {date} exists')
                continue

            trend = self.api.trend(code, t)

            time.sleep(0.5)

            if trend == None:
                logging.info(f'code: {code} date: {date} empty')
                continue

            date = datetime.fromtimestamp(trend[0]['time']).date().__str__()

            self.save(trend, code, date, filePath)

            logging.info(f'code: {code} date: {date} save trend')


# 個股產業分類與細分類
class Industry():
    def run(self, output):
        list = []
        resp = requests.get('https://www.moneydj.com/z/js/IndustryListNewJS.djjs', headers=HEADERS)
        resp.encoding = 'big5'
        resp = resp.text.split('var')[1].split('=')[1].split(';')
        for text in filter(None, resp):
            item = text.split('~')
            title = item[0].split(' ')

            for t in item[1].split(','):
                v = t.split(' ')
                stock = []

                logging.info(f' {title[-1]}-{v[1]}')

                list.append([title[-1], v[1]])

                resp = requests.get(f"https://www.moneydj.com/z/zh/zha/ZH00.djhtm?A={v[0]}", headers=HEADERS)
                time.sleep(1)

                for td in BeautifulSoup(resp.text, 'html.parser').find_all('td', id='oAddCheckbox'):
                    code = td.a.attrs['href'].split("'")[1][2:]
                    stock.append([code, td.text[len(code):]])

                dir = os.path.join(output, title[-1])

                if os.path.exists(dir) == False:
                    os.makedirs(dir)

                file_path = os.path.join(dir, v[1].replace('/', '_')) + '.csv'

                pd.DataFrame(stock, columns=['code', 'name']).to_csv(file_path, encoding="utf_8_sig", index=False)

        pd.DataFrame(list, columns=['industry', 'sub_industry']).to_csv(
            os.path.join(output, 'industry') + '.csv', encoding="utf_8_sig", index=False,
        )


# 概念股
class Concept():
    def run(self, output):
        resp = requests.get('https://www.moneydj.com/z/zg/zge_EH000237_1.djhtm')
        resp.encoding = 'big5'

        for value in BeautifulSoup(resp.text, 'html.parser').find_all('option'):
            if value.text == '1日':
                break

            resp = requests.get(f"https://www.moneydj.com/z/zg/zge_{value.attrs['value']}_1.djhtm")
            resp.encoding = 'big5'
            time.sleep(1)

            stock = []
            for td in BeautifulSoup(resp.text, 'html.parser').find_all('td', id='oAddCheckbox'):
                if len(td.contents) == 1:
                    continue

                v = td.contents[1].contents[0].split("'")
                stock.append([v[1][2:], v[3]])

            logging.info(value.text)

            pd.DataFrame(stock, columns=['code', 'name']).to_csv(
                os.path.join(output, value.text.replace('/', '_')) + '.csv', encoding="utf_8_sig", index=False,
            )


class api():
    def __init__(self):
        s = requests.session()
        resp = s.get('https://www.cmoney.tw')
        self._session = resp.cookies.get('AspSession')

        resp = s.get('https://www.cmoney.tw/notice/chart/stockchart.aspx?action=l&id=2330')
        ck = resp.text.split(';')[5].split('= ')[1]
        self._ck = ck[1:-1]

        self._time = int(time.time())

    # 抓取某個股某日trend
    def trend(self, code, date):
        resp = requests.get('https://www.cmoney.tw/notice/chart/stock-chart-service.ashx', params={
            'action': 'r',
            'id': code,
            'ck': self._ck,
            'date': date,
            '_': self._time,
        }, headers={
            'Referer': 'www.cmoney.tw',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
            'Cookie': 'AspSession=' + self._session
        })

        tData = []

        if resp.ok:
            try:
                tData = resp.json()['DataPrice']
            except json.decoder.JSONDecodeError as e:
                logging.error('code: ' + code + ' date: ' + date + ' error: ' + e.__str__())
                return None

        if len(tData) == 0:
            return None

        context = []

        # 將原始trend name重新命名
        for t in tData:
            if t[0] < 1300000000000:
                return None

            context.append({
                name.TIME: int(t[0] / 1000),
                name.CLOSE: t[1],
                name.VOLUME: t[2],
                name.HIGH: t[3],
                name.LOW: t[4],
            })

        return context


class Fund():
    type = [
        # 國內股票開放型指數型
        'ET000001',

        # 國內股票開放型科技類
        'ET001001',

        # 國內股票開放型中小型
        'ET001004',

        # 國內股票開放型一般股票型
        'ET001005',

        # 國內股票開放型中概股型
        'ET001006',

        # 國內股票開放型價值型
        'ET001007',

        # 國內股票開放型上櫃股票型
        'ET001008',

        # 股票債券平衡型一般股票型
        'ET004001',

        # 股票債券平衡型價值型股票型
        'ET004002',

    ]

    def to_csv(self, output):
        data = []
        codes = []
        dir = output
        file_path = output
        file = pd.DataFrame()

        for fund in self.get_fund():
            (company, code) = fund

            resp = requests.get(
                f'https://www.moneydj.com/funddj/ya/yp402002.djhtm?a={code}&b=803',
                headers=HEADERS
            )

            html = BeautifulSoup(resp.text, 'html.parser')
            date = html.find('div', class_='t3n1c1').text.split('：')[-1]
            date = f'{date[:4]}-{date[5:7]}-{date[8:]}'

            if file.empty:
                dir = os.path.join(output, f'{date[:4]}{date[5:7]}')
                file_path = os.path.join(dir, 'fund.csv')

                if os.path.exists(file_path):
                    file = pd.read_csv(os.path.join(output, f'{date[:4]}{date[5:7]}', 'fund.csv'))
                    codes = file['code'].tolist()

            for raws in html.find_all('tr')[6:]:
                value = raws.text.split('\n')

                if len(value) <= 2:
                    break

                if value[4] == 'N/A':
                    continue

                t_code = parse_qs(urlparse.urlparse(raws.contents[5].contents[0].get('href')).query)['a'][0]

                if t_code not in self.type:
                    continue

                code = parse_qs(urlparse.urlparse(raws.contents[3].contents[0].get('href')).query)['a'][0]
                name = value[2]
                type = value[3]

                if code in codes:
                    continue

                resp = requests.get(f'https://www.moneydj.com/funddj/yp/yp011000.djhtm?a={code}')
                table = BeautifulSoup(resp.text, 'html.parser').find('table', class_='t04')
                scale = table.contents[1].contents[6].contents[1].text.split()

                time.sleep(1)

                if len(scale) == 0:
                    continue

                data.append(
                    [name, company, type, code, scale[0][:-6], scale[0][-6:], date]
                )

                logging.info(f'{name} {code} {type} {date} {scale}')

        if os.path.exists(dir) == False:
            os.makedirs(dir)

        data = file.to_numpy().tolist() + data

        pd.DataFrame(
            data, columns=['name', 'company', 'type', 'code', 'amount', 'valuation', 'date']
        ).to_csv(file_path, index=False)

    def get_fund(self):
        fund = []
        resp = requests.get('https://www.moneydj.com/funddj/yb/YP303000.djhtm', headers=HEADERS)
        soup = BeautifulSoup(resp.text, 'html.parser').find_all('tr')

        for raws in soup[6:]:
            if len(raws.contents) <= 1:
                break

            name = raws.contents[1].text
            code = raws.contents[1].contents[0].get('href').split('=')[-1]
            fund.append([name, code])

        return fund
