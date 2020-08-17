import argparse
import os
from xq.item import run
from xq.imageDay import image as day
from xq.imageHistory import image as history

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

parser.add_argument(
    '-dayX',
    help='trend chart date for x',
    default=1,
    type=int
)

parser.add_argument(
    '-dayY',
    help='trend chart date for y',
    default=1,
    type=int
)

parser.add_argument(
    '-prevDay',
    help='Technical analysis a few days ago',
    default=0,
    type=int
)

parser.add_argument(
    '-prevMonth',
    help='Technical analysis a few Month ago',
    default=0,
    type=int
)

args = parser.parse_args()

if args.model == 'day':
    run(args.total, args.dir, day())

if args.model == 'history':
    run(args.total, args.dir, history(args.prevDay, args.prevMonth, args.dayX, args.dayY))
