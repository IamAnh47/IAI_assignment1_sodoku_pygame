from solve import Solver as DFSSolver
from solve_mrv import MRVSolver   # Sử dụng thuật toán MRV thay cho Min-Conflicts
from board import Board
import time
import tracemalloc
import os
import gen_input

def read_sudoku(filename):
    """
    Đọc file và trả về ma trận Sudoku 9x9.
    Mỗi dòng chứa 9 số cách nhau bởi khoảng trắng (0 đại diện cho ô trống).
    """
    sudoku = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                row = list(map(int, line.split()))
                sudoku.append(row)
    return sudoku

def write_board_to_file(board, filename):
    """
    Ghi ma trận Sudoku (lấy giá trị từ các cell) vào file.
    """
    with open(filename, "w") as f:
        for i in range(9):
            line = " ".join(str(board[i][j].get_value()) for j in range(9))
            f.write(line + "\n")

def main():
    level_files = ("basic.txt", "easy.txt", "intermediate.txt", "advance.txt", "extreme.txt", "evil.txt")
    level_names = ("basic", "easy", "intermediate", "advance", "extreme", "evil")

    while True:
        print("\nChọn level:")
        print("  1. Basic")
        print("  2. Easy")
        print("  3. Intermediate")
        print("  4. Advance")
        print("  5. Extreme")
        print("  6. Evil")
        inp = int(input("Lựa chọn: "))
        if inp in range(1, 7):
            break

    # Chọn chế độ: dùng bài toán có sẵn hay ngẫu nhiên
    while True:
        print("\nBạn muốn dùng bài toán có sẵn hay ngẫu nhiên?")
        print("  1. Có sẵn")
        print("  2. Ngẫu nhiên")
        mode = int(input("Lựa chọn: "))
        if mode in (1, 2):
            break

    if mode == 1:
        file_input = f"input/{level_files[inp - 1]}"
        init_board = read_sudoku(file_input)
    else:
        init_board, _ = gen_input.generate_input(inp)
        print(f"Đã sinh input ngẫu nhiên và lưu vào file input/{level_names[inp - 1]}_gen.txt")

    # Khởi tạo đối tượng Board và in ra bài toán ban đầu
    board_obj = Board(init_board)
    print("\nBài toán ban đầu:")
    board_obj.draw_grid()
    input("Ấn Enter để tiếp tục...")

    while True:
        print("\nChọn giải thuật để giải bài toán sudoku:")
        print("  1. DFS")
        print("  2. MRV")
        algo = int(input("Lựa chọn: "))
        if algo in (1, 2):
            break

    try:
        tracemalloc.start()
        start = time.time()

        if algo == 1:
            solver = DFSSolver(board_obj)
            if solver.solve_dfs(drawFlag=False):
                print("Giải thành công bằng DFS!")
            else:
                print("Giải không thành công với DFS")
        elif algo == 2:
            solver = MRVSolver(board_obj)
            if solver.solve_mrv(drawFlag=False):
                print("Giải thành công bằng MRV!")
            else:
                print("Giải không thành công với MRV")

        # In kết quả ra màn hình (bảng Sudoku đã được giải)
        print("\nKết quả cuối cùng:")
        board_obj.draw_grid()

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        time_run = time.time() - start
        memory_alloc = top_stats[0].size / 1024

        print(f"Thời gian: {time_run:.2f} s")
        print(f"Bộ nhớ: {memory_alloc:.2f} KB")

        # Lưu kết quả ra file output/.txt
        output_folder = "output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_filename = os.path.join(output_folder, f"{level_names[inp - 1]}.txt")
        write_board_to_file(board_obj.grid, output_filename)
        print(f"Kết quả đã được lưu vào file {output_filename}")

        user_input = int(input("Ấn \"1\" để chạy kết quả step-by-step: "))
        if user_input == 1:
            board_step = Board(init_board)
            if algo == 1:
                solver_step = DFSSolver(board_step)
                solver_step.solve_dfs(drawFlag=True)
            elif algo == 2:
                solver_step = MRVSolver(board_step)
                solver_step.solve_mrv(drawFlag=True)
            print(f"Thời gian: {time_run:.2f} s")
            print(f"Bộ nhớ: {memory_alloc:.2f} KB")
        else:
            return

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
