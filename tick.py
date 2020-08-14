import argparse
import logging
import os
from datetime import datetime
from ctick.tick import run

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=(datetime.now().strftime("%Y-%m-%d-tick.log")))
logging.getLogger().addHandler(logging.StreamHandler())

parser = argparse.ArgumentParser()
parser.add_argument(
    '-ck',
    help='cmoney api ck',
    default='EDEAQRQ0oPA3DNCAsDCbTJlfaYA8tO8v3WmfCMD3LHmrmJjB}DQM2M}JXG^rz',
    required=False,
    type=str
)

parser.add_argument(
    '-session',
    help='cmoney api session',
    default='z211g11uabjq2m4f2zyzjl2p',
    required=False,
    type=str
)

parser.add_argument(
    '-date',
    help='tick date',
    default=datetime.now().date().__str__(),
    type=str
)

parser.add_argument(
    '-dir',
    help='file dir',
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

run(args.date, args.ck, args.session, args.file, args.dir)
