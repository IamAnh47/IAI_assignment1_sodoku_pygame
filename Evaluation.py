import sys
import time
import threading
import os
import tracemalloc
import colorsys
from board import Board
from solve import Solver 
from solve_mrv import MRVSolver
from numpy import np

def measure_execution_time(algorithm, board, num_tests=100):
    times = []
    memories = []
    if algorithm.uppcase() =="DFS":
        solve = Solver(board)
    else:
        solve = MRVSolver(board)
    for _ in range(num_tests):
        start_time = time.time()
        tracemalloc.start()

        solve(board)  

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        measured_memory = top_stats[0].size / 1024 if top_stats else 0
        end_time = time.time()
        memories.append(measured_memory)
        times.append(end_time - start_time)  # Lưu thời gian thực thi
    return (np.mean(times),np.mean(memories))  # Trả về thời gian trung bình