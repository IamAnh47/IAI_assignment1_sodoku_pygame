from board import Board, Cell

class MRVSolver:
    def __init__(self, board: Board):
        self.board = board

    def find_empty_cell_mrv(self):
        """Tìm ô trống có số khả năng điền ít nhất (MRV)."""
        best_cell = None
        best_count = 10  # Số khả năng tối đa của một ô là 9
        for row in range(9):
            for col in range(9):
                if self.board.grid[row][col].value == 0:
                    count = 0
                    for num in range(1, 10):
                        if self.board.is_valid_cell(row, col, num):
                            count += 1
                    # Nếu không có khả năng điền nào, trả về ngay ô đó
                    if count == 0:
                        return (row, col)
                    if count < best_count:
                        best_count = count
                        best_cell = (row, col)
        return best_cell

    def solve_mrv(self, drawFlag=False):
        empty_cell = self.find_empty_cell_mrv()
        if not empty_cell:
            if drawFlag:
                self.board.draw_grid()
            return True  # Giải thành công khi không còn ô trống

        row, col = empty_cell
        for num in range(1, 10):
            if self.board.is_valid_cell(row, col, num):
                if drawFlag:
                    self.board.update_cell_draw(row, col, num)
                else:
                    self.board.grid[row][col].set_value(num)

                if self.solve_mrv(drawFlag):
                    return True

                # Quay lui nếu không giải được
                if drawFlag:
                    self.board.update_cell_draw(row, col, 0)
                else:
                    self.board.grid[row][col].set_value(0)
        return False
