import copy
import time

from src.load_data import load_puzzles
from src.sudoku import Rule


def is_valid(res):
    return 'timeout' if res == 0 else ('invalid' if res == 2 else 'solved')


if __name__ == '__main__':
    file_name = "../data/sudoku-problem.txt"
    puzzles = load_puzzles(file_name)

    solved = 0
    total_time = 0
    for puzzle in copy.deepcopy(puzzles):
        clock = time.time() * 1000
        value = puzzle.solve(rule_mask=Rule.SINGLES.value)
        clock = time.time() * 1000 - clock
        total_time = total_time + clock
        solved = solved + (1 if puzzle.is_valid() == 1 else 0)
        print('[%s] time(ms)=%d moves=%d backtracks=%d status=%s'
              % (puzzle.name, clock, value, puzzle.back, is_valid(puzzle.is_valid())))
    print('[Singles] Took %d ms to solve %d problems' % (total_time, solved))

    # solved = 0
    # total_time = 0
    # for puzzle in copy.deepcopy(puzzles):
    #     clock = time.time() * 1000
    #     value = puzzle.solve(rule_mask=Rule.SINGLES.value | Rule.PAIRS.value | Rule.TRIPLES.value)
    #     clock = time.time() * 1000 - clock
    #     total_time = total_time + clock
    #     solved = solved + (1 if puzzle.is_valid() == 1 else 0)
    #     print('[%s] time(ms)=%d moves=%d backtracks=%d status=%s'
    #           % (puzzle.name, clock, value, puzzle.back, is_valid(puzzle.is_valid())))
    # print('[Singles, Pairs, Triples] Took %d ms to solve %d problems' % (total_time, solved))
