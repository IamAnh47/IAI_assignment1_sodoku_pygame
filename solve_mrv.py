#solve_mrv.py
from board import Board, Cell
"""
Ở find_empty_cell_mrv:
   - Quét toàn bộ bảng sudoku.
   - Với mỗi 0 - tức là trống đó, đếm số lượng các số 1 -> 9 có thể được điền vào ô đó mà không vi phạm quy tắc sudoku 
   - Nếu count == 0, return ngay ô đó vì không thể giải được.
   - Save ô trống count min khả năng điền ít nhất - cũng là tốt nhất và return về ô đó.

Solve_mrv:
   - Gọi lại find_empty_cell_mrv để tìm ô trống có ít khả năng điền nhất.
   - Nếu không còn ô trống nào trả về True tức là đã dduocj giải.
   - Với ô trống được chọn, thử điền các số từ 1 đến 9:
       Nếu hợp lệ thì thực hiện:
           - Gọi đệ quy solve_mrv(drawFlag) để giải phần còn lại của bảng.
           - Nếu đệ quy trả về True -> return True.
           - Ngược lại, backtracking: reset ô đó về giá trị 0.
   - Nếu không tìm được số nào hợp lệ cho ô hiện tại, trả về False -> triggers quá trình quay lui.
"""

class MRVSolver:
    def __init__(self, board: Board):
        self.board = board

    def find_empty_cell_mrv(self):
        best_cell = None
        best_count = self.board.n + 1
        for row in range(self.board.n):
            for col in range(self.board.n):
                if self.board.grid[row][col].value == 0:
                    count = 0
                    for num in range(1, self.board.n + 1):
                        if self.board.is_valid_cell(row, col, num):
                            count += 1
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
            return True
        row, col = empty_cell
        for num in range(1, self.board.n + 1):
            if self.board.is_valid_cell(row, col, num):
                if drawFlag:
                    self.board.update_cell_draw(row, col, num)
                else:
                    self.board.grid[row][col].set_value(num)
                if self.solve_mrv(drawFlag):
                    return True
                if drawFlag:
                    self.board.update_cell_draw(row, col, 0)
                else:
                    self.board.grid[row][col].set_value(0)
        return False