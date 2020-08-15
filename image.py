import argparse
import os
from xq.item import run
from xq.imageDay import image as day

parser = argparse.ArgumentParser()

parser.add_argument(
    '-total',
    help='stock total',
    default=100,
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
    run(args.total, args.dir, day())
