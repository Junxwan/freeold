import argparse
import logging
import os
from datetime import datetime

from stock import weak

filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log',
                        datetime.now().strftime("%Y-%m-%d-stock.log"))

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=filename)
logging.getLogger().addHandler(logging.StreamHandler())

parser = argparse.ArgumentParser()

parser.add_argument(
    '-model',
    help='model',
    required=True,
    type=str
)

parser.add_argument(
    '-date',
    help='date',
    required=True,
    type=str
)

parser.add_argument(
    '-dataDir',
    help='data dir',
    required=True,
    type=str
)

parser.add_argument(
    '-output',
    help='output path',
    required=True,
    type=str
)

args = parser.parse_args()

logging.info('=================== ' + args.model + ' =================== ')

switch = {
    'weak': weak.run
}

switch[args.model](args.date, args.dataDir, args.output)
