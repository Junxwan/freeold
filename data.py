import argparse
import logging
import os
from datetime import datetime
import openpyxl
import crawler

from crawler.info import yahoo


def cmoneyTick(args):
    dates = []
    if os.path.isfile(args.cmDate):
        xlsx = openpyxl.load_workbook(args.cmDate)
        for cell in xlsx.active:
            if cell[0].value == None:
                continue

            dates.append(str(cell[0].value)[:10])
    else:
        dates.append(args.cmDate)

    for date in dates:
        crawler.cmoney.pullTick(date, args.cmCk, args.cmSession, args.file, args.dir)


filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log',
                        datetime.now().strftime("%Y-%m-%d-tick.log"))

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=filename)
logging.getLogger().addHandler(logging.StreamHandler())

parser = argparse.ArgumentParser()

parser.add_argument(
    '-model',
    help='crawler model',
    required=True,
    type=str
)

parser.add_argument(
    '-cmCk',
    help='cmoney api ck',
    default='EDEAQRQ0oPA3DNCAsDCbTJlfaYA8tO8v3WmfCMD3LHmrmJjB}DQM2M}JXG^rz',
    required=False,
    type=str
)

parser.add_argument(
    '-cmSession',
    help='cmoney api session',
    default='z211g11uabjq2m4f2zyzjl2p',
    required=False,
    type=str
)

parser.add_argument(
    '-cmDate',
    help='cmoney crawler date',
    default="D:\\free\open.xlsx",
    type=str
)

parser.add_argument(
    '-dir',
    help='dir',
    default=os.path.dirname(os.path.abspath(__file__)),
    type=str
)

parser.add_argument(
    '-file',
    help='code file',
    required=False,
    default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code.xlsx'),
    type=str
)

args = parser.parse_args()

if args.model == 'tick-cmoney':
    cmoneyTick(args)

if args.model == 'yahoo-info':
    yahoo.pullInfo(args.file, args.dir)
