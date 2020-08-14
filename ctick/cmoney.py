import json
import logging
import time

import requests

class Cmoney():
    def __init__(self, ck, session):
        self.__ck = ck
        self.__session = session
        self.__time = int(time.time())

    # 抓取某個股某日tick
    def tick(self, code, date):
        resp = requests.get('https://www.cmoney.tw/notice/chart/stock-chart-service.ashx', params={
            'action': 'r',
            'id': code,
            'ck': self.__ck,
            'date': date,
            '_': self.__time,
        }, headers={
            'Referer': 'www.cmoney.tw',
            'Cookie': 'AspSession=' + self.__session
        })

        tData = []

        if resp.ok:
            try:
                tData = resp.json()['DataPrice']
            except json.decoder.JSONDecodeError as e:
                logging.error('code: ' + code + ' date: ' + date + ' error: ' + e.__str__())
                return None

        context = []

        # 將原始tick name重新命名
        for t in tData:
            if t[0] < 1500000000000:
                return None

            context.append({
                'time': int(t[0] / 1000),
                'price': t[1],
                'volume': t[2],
                'max': t[3],
                'min': t[4],
            })

        return context
