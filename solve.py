from board import Board, Cell

class Solver:
    def __init__(self, board: Board):
        self.board = board

    def solve(self, drawFlag=False):
        empty_cell = self.board.find_empty_cell()
        if not empty_cell:
            if drawFlag:
                self.board.draw_grid()
            return True
        row, col = empty_cell
        for num in range(1, self.board.n + 1):
            if self.board.is_valid_cell(row, col, num):
                if drawFlag:
                    self.board.update_cell_draw(row, col, num)
                else:
                    self.board.grid[row][col].set_value(num)
                if self.solve(drawFlag):
                    return True
                if drawFlag:
                    self.board.update_cell_draw(row, col, 0)
                else:
                    self.board.grid[row][col].set_value(0)
        return False