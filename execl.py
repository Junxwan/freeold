import argparse
import logging
import os
from datetime import datetime

from xlsx.json import year

filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log',
                        datetime.now().strftime("%Y-%m-%d-xlsx.log"))

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=filename)
logging.getLogger().addHandler(logging.StreamHandler())

parser = argparse.ArgumentParser()
parser.add_argument(
    '-output',
    help='output path',
    required=True,
    type=str
)

parser.add_argument(
    '-input',
    help='input xlsx path',
    required=True,
    type=str
)

parser.add_argument(
    '-model',
    help='xlsx model',
    required=True,
    type=str
)

args = parser.parse_args()

if args.model == 'year-json':
    year.run(args.input, args.output)
