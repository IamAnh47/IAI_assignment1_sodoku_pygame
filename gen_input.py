import random
import os


def is_valid(board, row, col, num, n, block_rows, block_cols):
    if num in board[row]:
        return False
    for i in range(n):
        if board[i][col] == num:
            return False
    start_row, start_col = (row // block_rows) * block_rows, (col // block_cols) * block_cols
    for i in range(block_rows):
        for j in range(block_cols):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def generate_complete_board(n, block_rows, block_cols):
    board = [[0 for _ in range(n)] for _ in range(n)]

    def find_cell_with_fewest_candidates():
        best = None
        best_candidates = None
        for i in range(n):
            for j in range(n):
                if board[i][j] == 0:
                    candidates = []
                    for num in range(1, n + 1):
                        if is_valid(board, i, j, num, n, block_rows, block_cols):
                            candidates.append(num)
                    if not candidates:
                        return (i, j), []
                    if best is None or len(candidates) < len(best_candidates):
                        best = (i, j)
                        best_candidates = candidates
                        if len(best_candidates) == 1:
                            return best, best_candidates
        return best, best_candidates

    def fill():
        cell, candidates = find_cell_with_fewest_candidates()
        if cell is None:
            return True
        row, col = cell
        if not candidates:
            return False
        random.shuffle(candidates)
        for num in candidates:
            board[row][col] = num
            if fill():
                return True
            board[row][col] = 0
        return False

    fill()
    return board


def generate_puzzle(level, n, block_rows, block_cols):
    if n == 9:
        mapping = {1: 50, 2: 48, 3: 46, 4: 44, 5: 42, 6: 40}
    elif n == 12:
        mapping = {1: 90, 2: 86, 3: 82, 4: 78, 5: 74, 6: 70}
    elif n == 16:
        mapping = {1: 150, 2: 146, 3: 142, 4: 138, 5: 134, 6: 130}
    clues = mapping.get(level, mapping[1])
    complete_board = generate_complete_board(n, block_rows, block_cols)
    puzzle = [row[:] for row in complete_board]
    total_cells = n * n
    cells_to_remove = total_cells - clues
    positions = [(r, c) for r in range(n) for c in range(n)]
    random.shuffle(positions)
    for i in range(cells_to_remove):
        r, c = positions[i]
        puzzle[r][c] = 0
    return puzzle, complete_board


def generate_input(level, n=9, block_rows=3, block_cols=3, file=""):
    level_names = {1: "basic", 2: "easy", 3: "intermediate", 4: "advance", 5: "extreme", 6: "evil"}
    level_str = level_names.get(level, "basic")
    filename = f"input/{level_str}_{n}x{n}_random.txt" if file == "" else file
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    puzzle, solution = generate_puzzle(level, n, block_rows, block_cols)
    with open(filename, "w") as f:
        for row in puzzle:
            line = " ".join(str(num) for num in row)
            f.write(line + "\n")
    return puzzle, solution

