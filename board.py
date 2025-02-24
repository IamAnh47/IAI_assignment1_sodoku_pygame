import os
import time

class Cell:
    def __init__(self, value):
        self.value = value
        if value != 0:
            self.is_fixed = True  # Ô đã được điền
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
    def __init__(self, grid_init):
        # Tạo một lưới 9x9 gồm các Cell
        self.grid = [[Cell(grid_init[row][col]) for col in range(9)] for row in range(9)]

    def is_valid_cell(self, row, col, value):
        # Kiểm tra hàng và cột
        for i in range(9):
            if self.grid[row][i].value == value or self.grid[i][col].value == value:
                return False

        # Kiểm tra khối 3x3
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.grid[start_row + i][start_col + j].value == value:
                    return False
        return True

    def find_empty_cell(self):
        for row in range(9):
            for col in range(9):
                if self.grid[row][col].value == 0:
                    return (row, col)
        return None

    def color_text(self, text, color):
        COLORS = {
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "reset": "\033[0m",
        }
        return f"{COLORS[color]}{text}{COLORS['reset']}"

    def draw_grid(self, row=-1, col=-1):
        print(("+" + "-" * 7) * 3 + "+")
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print(("+" + "-" * 7) * 3 + "+")
            for j in range(10):
                if j % 3 == 0:
                    print("|", end=" ")
                if j != 9:
                    cell_value = self.grid[i][j].get_value()
                    ctx = cell_value if cell_value != 0 else "."
                    if i == row and j == col:
                        print(self.color_text(ctx, 'red'), end=" ")
                    elif self.grid[i][j].isfixed():
                        print(self.color_text(ctx, 'green'), end=" ")
                    else:
                        print(ctx, end=" ")
            print()
        print(("+" + "-" * 7) * 3 + "+")
        print()

    def update_cell_draw(self, row, col, value):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.grid[row][col].set_value(value)
        self.draw_grid(row, col)
        time.sleep(0.5)
