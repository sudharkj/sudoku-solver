# utils/load_data.py
from sudoku.__init__ import SuDoKu


def load_sudokus(file_name):
    """
    Loads SuDoKu puzzles from file with file name.
    :param file_name: file name
    :return: list of SuDoKu puzzles
    """
    puzzles = []
    with open(file_name) as file:
        lines = file.read().split()
        ind = 0
        while ind < len(lines):
            name = 'puzzle'
            rows = []
            for i in range(9):
                cols = []
                for j in range(3):
                    block = lines[ind + 3 * i + j]
                    for k in range(len(block)):
                        cols.append(int(block[k]))
                rows.append(cols)
            puzzle = SuDoKu(name, rows)
            puzzles.append(puzzle)
            ind = ind + 27
    return puzzles
