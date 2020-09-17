# -*- coding: utf-8 -*-

import json
import logging
import os
import time
import requests
import pandas as pd
from datetime import datetime


class Trend():
    def __init__(self, ck, session, dir):
        self.dir = dir
        self.api = api(ck, session)

    def get(self, date):
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
    def __init__(self, ck, session, code, dir):
        Trend.__init__(self, ck, session, dir)
        self.code = self.readCode(code)

    def readCode(self, path):
        return [c[0] for c in pd.read_csv(path, index_col=False, header=None).to_numpy().tolist()]

    def get(self, date):
        if self.code.__len__() == 0:
            logging.info('無個股代碼')
            return

        count = 0
        ok = 0
        failure = 0
        exists = 0
        emy = []

        t = str(date).replace('-', '')

        dir = os.path.join(self.dir, date[:4], date)

        if os.path.exists(dir) == False:
            os.makedirs(dir)

        for code in self.code:
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

            date = datetime.fromtimestamp(tData[0]['time']).date().__str__()

            if self.save(tData, code, date, filePath):
                ok += 1
                logging.info(f'code: {code} date: {date} save trend - {str(count)}')
            else:
                failure += 1
                logging.info(f'code: {code} date: {date} save failure - {str(count)}')

        logging.info(
            f"total: {self.code.__len__()} result: {ok + failure + exists + emy.__len__()} ok: {ok} failure: {failure} exists: {exists}"
        )
        logging.info(f"empty: {emy.__len__()} {emy.__str__()}")


class market(Trend):
    def __init__(self, ck, session, dir):
        Trend.__init__(self, ck, session, dir)

        tseDir = os.path.join(dir, 'tse')
        otcDir = os.path.join(dir, 'otc')
        self.code = {
            'TWA00': tseDir,
            'TWC00': otcDir,
        }

        for p in [tseDir, otcDir]:
            if os.path.exists(p) == False:
                os.makedirs(p)

    def get(self, date):
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

            time.sleep(1)

            if trend == None:
                logging.info(f'code: {code} date: {date} empty')
                continue

            date = datetime.fromtimestamp(trend[0]['time']).date().__str__()

            self.save(trend, code, date, filePath)

            logging.info(f'code: {code} date: {date} save trend')


class api():
    def __init__(self, ck, session):
        self.__ck = ck
        self.__session = session
        self.__time = int(time.time())

    # 抓取某個股某日trend
    def trend(self, code, date):
        resp = requests.get('https://www.cmoney.tw/notice/chart/stock-chart-service.ashx', params={
            'action': 'r',
            'id': code,
            'ck': self.__ck,
            'date': date,
            '_': self.__time,
        }, headers={
            'Referer': 'www.cmoney.tw',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
            'Cookie': 'AspSession=' + self.__session
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
                'time': int(t[0] / 1000),
                'price': t[1],
                'volume': t[2],
                'max': t[3],
                'min': t[4],
            })

        return context
