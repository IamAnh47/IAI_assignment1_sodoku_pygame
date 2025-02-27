import random
import os

def is_valid(board, row, col, num, n, block_rows, block_cols):
    if num in board[row]:
        return False
    for r in range(n):
        if board[r][col] == num:
            return False
    start_row, start_col = (row // block_rows) * block_rows, (col // block_cols) * block_cols
    for i in range(block_rows):
        for j in range(block_cols):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def generate_complete_board(n, block_rows, block_cols):
    board = [[0 for _ in range(n)] for _ in range(n)]
    def fill():
        for i in range(n):
            for j in range(n):
                if board[i][j] == 0:
                    nums = list(range(1, n+1))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(board, i, j, num, n, block_rows, block_cols):
                            board[i][j] = num
                            if fill():
                                return True
                            board[i][j] = 0
                    return False
        return True
    fill()
    return board

def generate_puzzle(level, n, block_rows, block_cols):
    if n == 9:
        mapping = {1: 40, 2: 36, 3: 32, 4: 28, 5: 24, 6: 22}
    elif n == 12:
        mapping = {1: 50, 2: 46, 3: 42, 4: 38, 5: 34, 6: 30}
    elif n == 16:
        mapping = {1: 80, 2: 74, 3: 68, 4: 62, 5: 56, 6: 50}
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

def generate_input(level, n=9, block_rows=3, block_cols=3,file = ""):
    level_names = {1:"basic", 2:"easy", 3:"intermediate", 4:"advance", 5:"extreme", 6:"evil"}
    level_str = level_names.get(level, "basic")
    filename = f"input/random/{level_str}_{n}x{n}_random.txt" if file == None else file
    puzzle, solution = generate_puzzle(level, n, block_rows, block_cols)
    with open(filename, "w") as f:
        for row in puzzle:
            line = " ".join(str(num) for num in row)
            f.write(line + "\n")
    return puzzle, solution

def generate_testcase(tesecases):
    level_names = {1:"basic", 2:"easy", 3:"intermediate", 4:"advance", 5:"extreme", 6:"evil"}
    for n in (9,12,16):
        if n == 9:
            block_rows = 3
            block_cols = 3
        elif n == 12:
            block_rows = 3
            block_cols = 4
        elif n == 16:
            block_rows = 4
            block_cols = 4
        for level in range(1,7):
            for i in range(tesecases):
                file_path = f"input/{n}x{n}/{level_names[level]}/teseCase_{i+1}.txt"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                puzzle, solution =generate_puzzle(level, n, block_rows, block_cols)
                with open(file_path, "w") as f:
                    for row in puzzle:
                        line = " ".join(str(num) for num in row)
                        f.write(line + "\n")
                
if __name__ == "__main__":
    generate_testcase(50)
