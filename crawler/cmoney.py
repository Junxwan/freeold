import json
import logging
import os
import time
from datetime import datetime
import openpyxl
import api.cmoney as cmoney


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
def pullTick(date, ck, session, file, dir):
    codes = readCode(file)

    if codes.__len__() == 0:
        logging.info('無個股代碼')
        return

    c = cmoney.new(ck, session)

    count = 0
    ok = 0
    failure = 0
    exists = 0
    emy = []

    logging.info('======================= start ' + date + ' =======================')

    t = str(date).replace('-', '')

    for code in codes:
        _, path = fileInfo(date, code, dir)

        count += 1

        if os.path.exists(path):
            exists += 1
            logging.info('code: ' + code + ' date: ' + date + ' exists - ' + str(count))
            continue

        tData = c.tick(code, t)

        time.sleep(2)

        if tData == None:
            logging.info('code: ' + code + ' date: ' + date + ' empty - ' + str(count))
            emy.append(code)
            continue

        date = datetime.fromtimestamp(tData[0]['time']).date().__str__()

        if save(tData, code, date, dir):
            ok += 1
            logging.info('code: ' + code + ' date: ' + date + ' save tick - ' + str(count))
        else:
            failure += 1
            logging.info('code: ' + code + ' date: ' + date + ' save failure - ' + str(count))

    logging.info(
        f"total: {codes.__len__()} result: {ok + failure + exists + emy.__len__()} ok: {ok} failure: {failure} exists: {exists}"
    )
    logging.info(f"empty: {emy.__len__()} {emy.__str__()}")
    logging.info('======================= end ' + date + ' =======================')


# 抓取並保存某個股某日tick
def save(context, code, date, dir):
    # 檢查檔案路徑並把資料寫入檔案中
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
    dir = os.path.join(dir, date)
    path = os.path.join(dir, str(code)) + ".json"

    return dir, path
