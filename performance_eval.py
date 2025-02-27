import time
import os
import tracemalloc
from board import Board
from solve import Solver as DFSSolver
from solve_mrv import MRVSolver
import gen_input

# Map difficulty level thành tên (cho Sudoku 9x9)
difficulty_map = {1: "basic", 2: "easy", 3: "intermediate", 4: "advance", 5: "extreme", 6: "evil"}


def evaluate_performance(difficulty, n, block_rows, block_cols, num_cases=100):
    """
    Đánh giá hiệu năng của DFS và MRV trên num_cases test case cho một kích thước và cấp độ cụ thể.
    :param difficulty: Số từ 1 đến 6 (cho 9x9) hoặc 1 (cho 12x12, 16x16)
    :param n: Kích thước Sudoku (9, 12, hoặc 16)
    :param block_rows: Số hàng trong block
    :param block_cols: Số cột trong block
    :param num_cases: Số test case cần đánh giá
    :return: (dfs_times, mrv_times, dfs_mems, mrv_mems)
    """
    dfs_times = []
    mrv_times = []
    dfs_mems = []
    mrv_mems = []

    for i in range(num_cases):
        # Sinh đề bài bằng gen_input (random)
        puzzle, _ = gen_input.generate_input(difficulty, n, block_rows, block_cols)

        # Đánh giá DFS
        board_dfs = Board(puzzle, n, block_rows, block_cols)
        solver_dfs = DFSSolver(board_dfs)
        tracemalloc.start()
        start_time = time.time()
        try:
            solver_dfs.solve_dfs(drawFlag=False)
        except Exception as e:
            print("DFS Exception:", e)
        elapsed = time.time() - start_time
        # Nếu vượt quá 20 giây, quy định thời gian là 20s
        if elapsed > 20:
            elapsed = 20
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        mem_usage = top_stats[0].size / 1024 if top_stats else 0
        dfs_times.append(elapsed)
        dfs_mems.append(mem_usage)
        tracemalloc.stop()

        # Đánh giá MRV trên cùng một đề bài
        board_mrv = Board(puzzle, n, block_rows, block_cols)
        solver_mrv = MRVSolver(board_mrv)
        tracemalloc.start()
        start_time = time.time()
        try:
            solver_mrv.solve_mrv(drawFlag=False)
        except Exception as e:
            print("MRV Exception:", e)
        elapsed = time.time() - start_time
        if elapsed > 20:
            elapsed = 20
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        mem_usage = top_stats[0].size / 1024 if top_stats else 0
        mrv_times.append(elapsed)
        mrv_mems.append(mem_usage)
        tracemalloc.stop()

        print(f"Test case {i + 1}/{num_cases} hoàn thành.")
    return dfs_times, mrv_times, dfs_mems, mrv_mems


def save_results(directory, filename, data):
    """
    Lưu kết quả (một danh sách các giá trị) vào file.
    Mỗi dòng chứa một giá trị.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, filename)
    with open(path, "w") as f:
        for value in data:
            f.write(f"{value}\n")


def main():
    # Đánh giá cho Sudoku 9x9 với tất cả các cấp độ
    for diff in range(1, 7):
        print(f"Đang đánh giá 9x9, cấp độ: {difficulty_map[diff]}")
        dfs_times, mrv_times, dfs_mems, mrv_mems = evaluate_performance(diff, 9, 3, 3, num_cases=100)
        time_data = [f"{dfs_times[i]},{mrv_times[i]}" for i in range(100)]
        mem_data = [f"{dfs_mems[i]},{mrv_mems[i]}" for i in range(100)]
        save_results("time/9x9", f"{difficulty_map[diff]}.txt", time_data)
        save_results("memory/9x9", f"{difficulty_map[diff]}.txt", mem_data)

    # Đánh giá cho Sudoku 12x12 (chỉ cấp độ Basic)
    print("Đang đánh giá 12x12, cấp độ: basic")
    dfs_times, mrv_times, dfs_mems, mrv_mems = evaluate_performance(1, 12, 3, 4, num_cases=100)
    time_data = [f"{dfs_times[i]},{mrv_times[i]}" for i in range(100)]
    mem_data = [f"{dfs_mems[i]},{mrv_mems[i]}" for i in range(100)]
    save_results("time/12x12", "basic.txt", time_data)
    save_results("memory/12x12", "basic.txt", mem_data)

    # Đánh giá cho Sudoku 16x16 (chỉ cấp độ Basic)
    print("Đang đánh giá 16x16, cấp độ: basic")
    dfs_times, mrv_times, dfs_mems, mrv_mems = evaluate_performance(1, 16, 4, 4, num_cases=100)
    time_data = [f"{dfs_times[i]},{mrv_times[i]}" for i in range(100)]
    mem_data = [f"{dfs_mems[i]},{mrv_mems[i]}" for i in range(100)]
    save_results("time/16x16", "basic.txt", time_data)
    save_results("memory/16x16", "basic.txt", mem_data)


if __name__ == "__main__":
    main()
