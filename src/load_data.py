from src.sudoku import Sudoku


def load_puzzles(file_name):
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
            puzzle = Sudoku(name, rows)
            puzzles.append(puzzle)
            ind = ind + 27
    return puzzles
