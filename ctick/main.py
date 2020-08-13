# -*- coding: UTF-8 -*-

import os
import argparse
import time
from datetime import datetime
import json
import requests
import openpyxl
import logging


# 個股清單
def readCode():
    codes = []
    xlsx = openpyxl.load_workbook('code.xlsx')
    for cell in xlsx.active:
        if cell[0].value == None:
            continue

        codes.append(str(cell[0].value))
    return codes


# 抓取某個股某日tick
def tick(code, ck, date=''):
    resp = requests.get('https://www.cmoney.tw/notice/chart/stock-chart-service.ashx', params={
        'action': 'r',
        'id': code,
        'ck': ck,
        'date': date,
        '_': int(time.time()),
    }, headers={
        'Referer': 'www.cmoney.tw',
        'Cookie': '__auc=94620d3716d148ba5eec3847811; __gads=ID=c164e0debe3ffcd6:T=1568007759:S=ALNI_MZjFxiYuyO_VQH42cZMzYQ88X2O0w; _ga=GA1.2.1797485150.1568007760; _fbp=fb.1.1568007760792.1640624592; _hjid=c51e4be6-81f8-4f28-8b42-9e5256ed733b; dable_uid=28826945.1559268130950; NoPromptForFbBindingList=,KJRbTGoooXnAABCAiE8rEJAN2EAb7; fbm_428588507236817=base_domain=.www.cmoney.tw; _fbc=fb.1.1573525200781.IwAR3zKprh4cdHueoxRjzuYIQc-M7TFSVNz-1Nug7qR7clxPekcgPoziO73SM; _ss_pp_id=7a0bb3bf961c005aed1313bcbdcfe642; AviviD_uuid=958435bb-9dfc-492d-a2d7-f645a413a40b; webuserid=f444ba64-6b03-3e41-e6ac-9e3676d38c37; start=1; AviviD_canv=0; AviviD_refresh_uuid_status=2; AviviD_already_exist=1; AviviD_waterfall_status=0; __retuid=bfd7f957-721d-4618-8adc-4d9cd40f7af3; truvid_protected={"val":"c","level":2,"geo":"TW","timestamp":1595317916}; AspSession=s22rpud5vfkkm1junc5f4suq; ASP.NET_SessionId=1cbaj1by0s2wzpt2i2vgvq3u; _td=e1d56f00-73ca-46ec-8074-324b4b7cbe51; __asc=3d13a192173dcaaf0606ec0fa88; _gid=GA1.2.258296088.1597135057; AviviD_show_sub=1; _hjAbsoluteSessionInProgress=1; _gat_real=1; _gat_UA-30929682-4=1; _gat_UA-30929682-1=1; _gat_UA-30929682-32=1; page_view=4; GED_PLAYLIST_ACTIVITY=W3sidSI6IjlDQkgiLCJ0c2wiOjE1OTcxMzU2NTUsIm52IjowLCJ1cHQiOjE1OTY2OTc0ODUsImx0IjoxNTk3MTExNDg0fV0.',
    })

    if resp.ok:
        try:
            return resp.json()['DataPrice']
        except json.decoder.JSONDecodeError as e:
            logging.error('code: ' + code + ' date: ' + date + ' error: ' + e.__str__())

    return None


# 執行抓取tick資料
def run(date, ck):
    codes = readCode()

    if codes.__len__() == 0:
        logging.info('無個股代碼')
        return

    for code in codes:
        if save(code, ck, date):
            logging.info('code: ' + code + ' date: ' + date + ' 保存tick資料')
        else:
            logging.info('code: ' + code + ' date: ' + date + ' 無資料')

        time.sleep(5)


# 抓取並保存某個股某日tick
def save(code, ck, date):
    tData = tick(code, ck, date.replace('-', ''))

    if tData == None:
        return False

    context = []

    # 將原始tick name重新命名
    for t in tData:
        if t[0] < 1500000000000:
            return False

        context.append({
            'time': int(t[0] / 1000),
            'price': t[1],
            'volume': t[2],
            'max': t[3],
            'min': t[4],
        })

    # 檢查檔案路徑並把資料寫入檔案中
    date = datetime.fromtimestamp(context[0]['time']).date().__str__()
    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), str(code))
    path = os.path.join(dir, date) + ".json"

    if os.path.exists(dir) == False:
        os.mkdir(dir)

    if os.path.exists(path):
        return True

    f = open(path, 'w+')
    f.write(json.dumps({
        'code': code,
        'date': date,
        'data': context,
    }))
    f.close()

    return True


# main
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=(datetime.now().strftime("%Y-%m-%d.log")))
    logging.getLogger().addHandler(logging.StreamHandler())

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-ck',
        help='cmoney api ck',
        default='HGF$1M7ZnXUA6NTraECEfK{7TBRjAGBbALljuRmIn5T7FP9v{P7vDID3pNErz',
        required=False,
        type=str
    )
    parser.add_argument(
        '-date',
        help='tick date',
        default=datetime.now().date().__str__(),
        type=str
    )
    args = parser.parse_args()

    run(args.date, args.ck)
