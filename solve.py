from board import Board, Cell

class Solver:
    def __init__(self, board: Board):
        self.board = board

    def set_cell(self, row, col, value, drawFlag):
        if drawFlag:
            self.board.update_cell_draw(row, col, value)
        else:
            self.board.grid[row][col].set_value(value)

    def solve(self, drawFlag=False):
        board = self.board
        n = board.n
        empty = board.find_empty_cell()
        if empty is None:
            if drawFlag:
                board.draw_grid()
            return True

        row, col = empty
        for num in range(1, n + 1):
            if board.is_valid_cell(row, col, num):
                self.set_cell(row, col, num, drawFlag)
                if self.solve(drawFlag):
                    return True
                self.set_cell(row, col, 0, drawFlag)
        return False
