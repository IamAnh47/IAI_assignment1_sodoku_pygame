import os
import time

class Cell:
    def __init__(self, value):
        self.value = value
        if value != 0:
            self.is_fixed = True
        else:
            self.is_fixed = False

    def set_value(self, new_value):
        if not self.is_fixed:
            self.value = new_value

    def get_value(self):
        return self.value

    def isfixed(self) -> bool:
        return self.is_fixed

class Board:
    def __init__(self, grid_init, n=9, block_rows=3, block_cols=3):
        self.n = n
        self.block_rows = block_rows
        self.block_cols = block_cols
        self.grid = [[Cell(grid_init[row][col]) for col in range(n)] for row in range(n)]

    def is_valid_cell(self, row, col, value):
        for i in range(self.n):
            if self.grid[row][i].value == value or self.grid[i][col].value == value:
                return False
        start_row = (row // self.block_rows) * self.block_rows
        start_col = (col // self.block_cols) * self.block_cols
        for i in range(self.block_rows):
            for j in range(self.block_cols):
                if self.grid[start_row + i][start_col + j].value == value:
                    return False
        return True

    def find_empty_cell(self):
        for row in range(self.n):
            for col in range(self.n):
                if self.grid[row][col].value == 0:
                    return (row, col)
        return None

    def draw_grid(self, row=-1, col=-1):
        print(("+" + "-" * 7) * self.block_cols + "+")
        for i in range(self.n):
            if i % self.block_rows == 0 and i != 0:
                print(("+" + "-" * 7) * self.block_cols + "+")
            for j in range(self.n + 1):
                if j % self.block_cols == 0:
                    print("|", end=" ")
                if j != self.n:
                    cell_value = self.grid[i][j].get_value()
                    ctx = cell_value if cell_value != 0 else "."
                    if i == row and j == col:
                        print(ctx, end=" ")
                    elif self.grid[i][j].isfixed():
                        print(self.color_text(ctx, 'green'), end=" ")
                    else:
                        print(ctx, end=" ")
            print()
        print(("+" + "-" * 7) * self.block_cols + "+")
        print()

    def color_text(self, text, color):
        COLORS = {
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "reset": "\033[0m",
        }
        return f"{COLORS[color]}{text}{COLORS['reset']}"

    def update_cell_draw(self, row, col, value):
        # os.system('cls' if os.name == 'nt' else 'clear')
        self.grid[row][col].set_value(value)
        # self.draw_grid(row, col)
        # time.sleep(0.001)
