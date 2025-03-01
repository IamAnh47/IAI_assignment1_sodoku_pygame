from board import Board, Cell

class LCVSolver:
    def __init__(self, board: Board, lazy_neighbors=True):
        self.board = board
        self.n = board.n
        self.block_rows = board.block_rows
        self.block_cols = board.block_cols
        self.lazy_neighbors = lazy_neighbors
        if not self.lazy_neighbors:
            self.neighbors = {}
            self._precompute_neighbors()

    def _precompute_neighbors(self):
        n, br, bc = self.n, self.block_rows, self.block_cols
        for i in range(n):
            for j in range(n):
                cell_neighbors = []
                for col in range(n):
                    if col != j:
                        cell_neighbors.append((i, col))
                for row in range(n):
                    if row != i:
                        cell_neighbors.append((row, j))
                block_start_row = (i // br) * br
                block_start_col = (j // bc) * bc
                for r in range(block_start_row, block_start_row + br):
                    for c in range(block_start_col, block_start_col + bc):
                        if (r, c) != (i, j):
                            cell_neighbors.append((r, c))
                self.neighbors[(i, j)] = tuple(set(cell_neighbors))

    def _get_neighbors(self, row, col):
        if self.lazy_neighbors:
            n, br, bc = self.n, self.block_rows, self.block_cols
            cell_neighbors = []
            for col2 in range(n):
                if col2 != col:
                    cell_neighbors.append((row, col2))
            for row2 in range(n):
                if row2 != row:
                    cell_neighbors.append((row2, col))
            block_start_row = (row // br) * br
            block_start_col = (col // bc) * bc
            for r in range(block_start_row, block_start_row + br):
                for c in range(block_start_col, block_start_col + bc):
                    if (r, c) != (row, col):
                        cell_neighbors.append((r, c))
            return tuple(set(cell_neighbors))
        else:
            return self.neighbors[(row, col)]

    def _select_unassigned_cell(self):
        board = self.board
        n = self.n
        min_count = None
        selected = None
        selected_candidates = None
        for i in range(n):
            for j in range(n):
                if board.grid[i][j].get_value() == 0:
                    candidates = []
                    for v in range(1, n + 1):
                        if board.is_valid_cell(i, j, v):
                            candidates.append(v)
                    count = len(candidates)
                    if count == 0:
                        return (i, j), []
                    if min_count is None or count < min_count:
                        min_count = count
                        selected = (i, j)
                        selected_candidates = candidates
                        if min_count == 1:
                            return selected, selected_candidates
        return selected, selected_candidates

    def order_values_lcv(self, row, col, candidate_list=None):
        n = self.n
        board = self.board
        grid = board.grid
        neighbors = self._get_neighbors(row, col)
        candidates = []
        if candidate_list is None:
            candidate_list = [v for v in range(1, n + 1) if board.is_valid_cell(row, col, v)]
        for v in candidate_list:
            constraint = 0
            for (i, j) in neighbors:
                if grid[i][j].get_value() == 0 and board.is_valid_cell(i, j, v):
                    constraint += 1
            candidates.append((v, constraint))
        candidates.sort(key=lambda x: x[1])
        return [v for v, _ in candidates]

    def solve(self, drawFlag=False):
        board = self.board
        empty_cell, candidate_list = self._select_unassigned_cell()
        if empty_cell is None:
            if drawFlag:
                board.draw_grid()
            return True
        row, col = empty_cell
        candidates = self.order_values_lcv(row, col, candidate_list)
        for v in candidates:
            if board.is_valid_cell(row, col, v):
                if drawFlag:
                    board.update_cell_draw(row, col, v)
                else:
                    board.grid[row][col].set_value(v)
                if self.solve(drawFlag):
                    return True
                if drawFlag:
                    board.update_cell_draw(row, col, 0)
                else:
                    board.grid[row][col].set_value(0)
        return False
