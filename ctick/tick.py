# -*- coding: UTF-8 -*-

import os
import time
from datetime import datetime
import json
import openpyxl
import logging
from . import cmoney


# 個股清單
def readCode(path):
    codes = []
    xlsx = openpyxl.load_workbook(path)
    for cell in xlsx.active:
        if cell[0].value == None:
            continue

        codes.append(str(cell[0].value))
    return codes


# 執行抓取tick資料
def run(date, ck, session, file, dir):
    codes = readCode(file)

    if codes.__len__() == 0:
        logging.info('無個股代碼')
        return

    c = cmoney.Cmoney(ck, session)

    count = 0
    for code in codes:
        dir, path = fileInfo(date, code, dir)

        count += 1

        if os.path.exists(path):
            logging.info('code: ' + code + ' date: ' + date + ' exists - ' + str(count))
            continue

        tData = c.tick(code, date)

        time.sleep(3)

        if tData == None:
            logging.info('code: ' + code + ' date: ' + date + ' empty - ' + str(count))
            continue

        if save(tData, code, dir):
            logging.info('code: ' + code + ' date: ' + date + ' save tick - ' + str(count))
        else:
            logging.info('code: ' + code + ' date: ' + date + ' save failure - ' + str(count))


# 抓取並保存某個股某日tick
def save(context, code, dir):
    # 檢查檔案路徑並把資料寫入檔案中
    date = datetime.fromtimestamp(context[0]['time']).date().__str__()
    dir, path = fileInfo(date, code, dir)

    if os.path.exists(dir) == False:
        os.mkdir(dir)

    if os.path.exists(path):
        return True

    f = open(path, 'w+')
    f.write(json.dumps({
        'code': code,
        'date': date,
        'tick': context,
    }))
    f.close()

    return True


def fileInfo(date, code, dir):
    dir = os.path.join(dir, str(code))
    path = os.path.join(dir, date) + ".json"

    return dir, path
