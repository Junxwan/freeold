import argparse
import os
from xq.item import run
from xq.imageDay import image as day
from xq.imageHistory import image as history

parser = argparse.ArgumentParser()

parser.add_argument(
    '-dir',
    help='file dir',
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
    '-xqTotal',
    help='stock total',
    default=100,
    type=int
)

parser.add_argument(
    '-xqDayX',
    help='trend chart date for xq x',
    default=1,
    type=int
)

parser.add_argument(
    '-xqDayY',
    help='trend chart date for xq y',
    default=1,
    type=int
)

parser.add_argument(
    '-xqPrevDay',
    help='Technical analysis a few days ago for xq',
    default=0,
    type=int
)

parser.add_argument(
    '-xqPrevMonth',
    help='Technical analysis a few Month ago for xq',
    default=0,
    type=int
)

args = parser.parse_args()

if args.model == 'xq-day-image':
    run(args.xqTotal, args.dir, day())

if args.model == 'xq-history-image':
    run(args.xqTotal, args.dir, history(args.xqPrevDay, args.xqPrevMonth, args.xqDayX, args.xqDayY))
