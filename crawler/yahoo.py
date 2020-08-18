import logging
import math
import os
import time
from datetime import datetime
import openpyxl
import requests
from bs4 import BeautifulSoup


# 個股基本資料
def pullInfo(input, output):
    wb = openpyxl.Workbook()
    newSheet = wb.active
    xlsx = openpyxl.load_workbook(input)
    sheet = xlsx.active

    for code in sheet.iter_rows():
        industryName = ''
        product = []

        code = str(code[0].value)
        resp = requests.get('https://tw.stock.yahoo.com/d/s/company_' + code + '.html')

        if resp.status_code != 200:
            logging.info(code + ' empty')
        else:
            logging.info(code + ' get')

            soup = BeautifulSoup(resp.text, 'html.parser')
            tds = soup.select('table')[2].findAll('td')

            industryName = tds[3].text.strip()
            revenues = tds[31].text.lstrip().split('、')
            revenues[-1] = revenues[-1].partition('%')[0] + '%'

            for i, name in enumerate(revenues):
                for ii, s in enumerate(name):
                    if s.isdigit():
                        r = math.floor(float(name[ii:-1]))
                        if r >= 1:
                            product.append(name[:ii] + '-' + str(r))
                        break

        for column in range(0, sheet.max_row):
            newSheet.append([code, industryName, ','.join(product)])

        time.sleep(0.1)

    wb.save(os.path.join(output, "yahoo-info.xlsx"))
