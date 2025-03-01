import os
import glob
import re
import time
import tracemalloc
import concurrent.futures
import pandas as pd
import multiprocessing as mp

from board import Board
from solve import Solver
from solve_lcv import LCVSolver

def run_solver_on_testcase(test_file, solver_type):
    with open(test_file, 'r') as f:
        puzzle = [list(map(int, line.strip().split())) for line in f if line.strip()]
    n = len(puzzle)
    if n == 9:
        block_rows, block_cols = 3, 3
    elif n == 12:
        block_rows, block_cols = 3, 4
    elif n == 16:
        block_rows, block_cols = 4, 4
    else:
        raise ValueError("Unsupported board size")

    board = Board(puzzle, n, block_rows, block_cols)

    if solver_type == "DFS":
        solver = Solver(board)
    elif solver_type == "LCV":
        solver = LCVSolver(board)
    else:
        raise ValueError("Invalid solver type")

    tracemalloc.start()
    tracemalloc.reset_peak()
    start_time = time.perf_counter()

    solved = solver.solve()
    elapsed = time.perf_counter() - start_time
    current, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_memory_kb = peak_memory / 1024.0

    return (elapsed, peak_memory_kb, solved)

def evaluate_testcases():
    tasks = []
    results = []
    levels = ["basic", "easy", "intermediate", "advance", "extreme", "evil"]
    for level in levels:
        folder = os.path.join("input", "9x9", level)
        all_files = glob.glob(os.path.join(folder, "*.txt"))
        pattern_str = f"^{level}_[1-9][0-9]*\\.txt$"
        test_files = [f for f in all_files if re.match(pattern_str, os.path.basename(f))]
        test_files.sort()
        for solver_type in ["DFS", "LCV"]:
            for test_file in test_files:
                tasks.append({
                    "group": f"9x9-{level}",
                    "test_file": test_file,
                    "solver_type": solver_type
                })

    # 12x12 và 16x16 (chỉ cấp basic)
    for size in [12, 16]:
        folder = os.path.join("input", f"{size}x{size}", "basic")
        all_files = glob.glob(os.path.join(folder, "*.txt"))
        pattern_str = r"^basic_[1-9][0-9]*\.txt$"
        test_files = [f for f in all_files if re.match(pattern_str, os.path.basename(f))]
        test_files.sort()
        for solver_type in ["DFS", "LCV"]:
            for test_file in test_files:
                tasks.append({
                    "group": f"{size}x{size}-basic",
                    "test_file": test_file,
                    "solver_type": solver_type
                })

    total_tasks = len(tasks)
    print(f"Total tasks: {total_tasks}")
    with concurrent.futures.ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        future_to_task = {
            executor.submit(run_solver_on_testcase, task["test_file"], task["solver_type"]): task
            for task in tasks
        }
        completed = 0
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            group = task["group"]
            test_file = task["test_file"]
            solver_type = task["solver_type"]
            try:
                result = future.result(timeout=2)
            except concurrent.futures.TimeoutError:
                print(f"[Timeout] {solver_type}: Test case {os.path.basename(test_file)} exceeded 2 seconds.", flush=True)
                result = (2, 0, False)
            results.append({
                "Puzzle": group,
                "Testcase": os.path.basename(test_file),
                "Algorithm": solver_type,
                "Result": result
            })
            completed += 1
            print(f"{solver_type}: Finished {completed}/{total_tasks} tasks (Group: {group})", flush=True)
    return results

def aggregate_results(results):
    agg = {}
    for entry in results:
        key = (entry["Puzzle"], entry["Algorithm"])
        result = entry["Result"]
        if key not in agg:
            agg[key] = {"total_time": 0, "total_memory": 0, "solved_count": 0, "unsolved_count": 0, "total": 0}
        agg[key]["total"] += 1
        if result[2]:
            agg[key]["total_time"] += result[0]
            agg[key]["total_memory"] += result[1]
            agg[key]["solved_count"] += 1
        else:
            agg[key]["unsolved_count"] += 1

    aggregated = []
    for (puzzle, algo), data in agg.items():
        count = data["solved_count"]
        if count > 0:
            avg_time = data["total_time"] / count
            avg_memory = data["total_memory"] / count
        else:
            avg_time = None
            avg_memory = None
        aggregated.append({
            "Puzzle": puzzle,
            "Algorithm": algo,
            "AvgTime (s)": avg_time,
            "AvgMemory (Kb)": avg_memory,
            "SolvedCount": data["solved_count"],
            "UnsolvedCount": data["unsolved_count"],
            "TotalTestcases": data["total"]
        })
    return pd.DataFrame(aggregated)

def save_results_to_excel(df, filename="evaluation_results.xlsx"):
    df.to_excel(filename, index=False)
    print("Kết quả đã được lưu vào file", filename, flush=True)

def main():
    results = evaluate_testcases()
    df = aggregate_results(results)
    save_results_to_excel(df)

if __name__ == "__main__":
    mp.freeze_support()
    main()
