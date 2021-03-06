import argparse
import logging

from aoc.helpers import Puzzle

log = logging.getLogger(__name__)

# Define general parser
parser = argparse.ArgumentParser(description='Advent of Code 2020 — Solution Runner')

# Add option to provide solution by day number or by full path
day_group = parser.add_mutually_exclusive_group(required=True)
day_group.add_argument(
    "--day",
    type=Puzzle,
    dest="puzzle",
    help="select a puzzle by day number"
)
day_group.add_argument(
    "--path",
    type=Puzzle.from_path,
    dest="puzzle",
    help="select a puzzle by solution path"
)
day_group.add_argument(
    "--date",
    action="store_const",
    const=Puzzle.from_date(),
    dest="puzzle",
    help="select a puzzle by the current date (only work during the event)"
)

parser.add_argument('--debug', action='store_true', help='set logging level to DEBUG')
parser.add_argument(
    '--init', '--create',
    action='store_true',
    help='initialize the puzzle, but do not run it',
    dest="init_only"
)
parser.add_argument("--time", action='store_true', help="profile the running time using `timeit`")
parser.add_argument("--submit", action='store_true', help="submit the latest submission")
parser.add_argument(
    "--ignore-cache",
    action='store_true',
    help="submit the latest submission",
    dest="ignore_cache",
)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.debug:
        log.info("setting logging level to DEBUG")
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

    if args.init_only:
        log.info(f"initialized {args.puzzle}")
    elif args.time:
        log.info("starting timed run")
        args.puzzle.time()
    else:
        args.puzzle.run(submit=args.submit, ignore_cache=args.ignore_cache)
