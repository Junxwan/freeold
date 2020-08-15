import argparse
import os
from xq.imageDay import run as day

parser = argparse.ArgumentParser()

parser.add_argument(
    '-total',
    help='stock total',
    required=True,
    type=int
)

parser.add_argument(
    '-dir',
    help='image dir',
    default=os.path.dirname(os.path.abspath(__file__)),
    type=str
)

parser.add_argument(
    '-model',
    help='image model',
    default='day',
    type=str
)

args = parser.parse_args()

if args.model == 'day':
    day(args.total, args.dir)
