import random

def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    for r in range(9):
        if board[r][col] == num:
            return False
    start_row, start_col = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def generate_complete_board():
    board = [[0 for _ in range(9)] for _ in range(9)]
    def fill():
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(board, i, j, num):
                            board[i][j] = num
                            if fill():
                                return True
                            board[i][j] = 0
                    return False
        return True
    fill()
    return board

def generate_puzzle(level):
    """
    Sinh puzzle dựa trên bảng đã hoàn chỉnh.
    Cấp độ tương ứng với số ô gợi ý:
      1: Basic        -> 40 clues
      2: Easy         -> 36 clues
      3: Intermediate -> 32 clues
      4: Advance      -> 28 clues
      5: Extreme      -> 24 clues
      6: Evil         -> 22 clues
    """
    mapping = {1: 40, 2: 36, 3: 32, 4: 28, 5: 24, 6: 22}
    clues = mapping.get(level, 40)
    complete_board = generate_complete_board()
    puzzle = [row[:] for row in complete_board]
    total_cells = 81
    cells_to_remove = total_cells - clues

    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)
    for i in range(cells_to_remove):
        r, c = positions[i]
        puzzle[r][c] = 0

    return puzzle, complete_board

def generate_input(level):
    """
    Sinh ra puzzle ngẫu nhiên theo cấp độ, ghi vào file input/<level>_gen.txt.
    Trả về puzzle và solution.
    """
    level_names = {1: "basic", 2: "easy", 3: "intermediate",
                   4: "advance", 5: "extreme", 6: "evil"}
    puzzle, solution = generate_puzzle(level)
    filename = f"input/{level_names.get(level, 'basic')}_gen.txt"
    with open(filename, "w") as f:
        for row in puzzle:
            line = " ".join(str(num) for num in row)
            f.write(line + "\n")
    return puzzle, solution
