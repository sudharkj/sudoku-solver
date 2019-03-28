# app.py
import copy
import time

from sudoku.rule import Rule
from utils.load_data import load_sudokus
from utils.status import Status

if __name__ == '__main__':
    file_name = "data/sudoku-problem.txt"
    puzzles = load_sudokus(file_name)

    solved = 0
    total_time = 0
    for puzzle in copy.deepcopy(puzzles):
        clock = time.time() * 1000
        value = puzzle.solve(rule_mask=Rule.SINGLES.value|Rule.PAIRS.value|Rule.TRIPLES.value)
        clock = time.time() * 1000 - clock
        total_time = total_time + clock
        solved = solved + (1 if puzzle.status is Status.SOLVED else 0)
        print('[%s] time(ms)=%d moves=%d backtracks=%d status=%s'
              % (puzzle.name, clock, value[0], value[1], puzzle.status.name))
    print('[Singles] Took %d ms to solve %d problems' % (total_time, solved))
