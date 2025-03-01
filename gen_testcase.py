import os
import concurrent.futures
from gen_input import generate_input


def generate_testcase(params):
    level, n, block_rows, block_cols, file_path = params
    if not os.path.exists(file_path):
        generate_input(level, n, block_rows, block_cols, file=file_path)
        return f"Generated {file_path}"
    else:
        return f"{file_path} đã tồn tại, bỏ qua."


def create_test_cases(num=50):
    level_names = {1: "basic", 2: "easy", 3: "intermediate", 4: "advance", 5: "extreme", 6: "evil"}
    tasks = []

    n = 9
    br, bc = 3, 3
    for level in range(1, 7):
        level_str = level_names[level]
        folder = os.path.join("input", "9x9", level_str)
        os.makedirs(folder, exist_ok=True)
        for i in range(1, num + 1):
            file_path = os.path.join(folder, f"{level_str}_{i}.txt")
            tasks.append((level, n, br, bc, file_path))

    n = 12
    br, bc = 3, 4
    folder = os.path.join("input", "12x12", "basic")
    os.makedirs(folder, exist_ok=True)
    for i in range(1, num + 1):
        file_path = os.path.join(folder, f"basic_{i}.txt")
        tasks.append((1, n, br, bc, file_path))

    n = 16
    br, bc = 4, 4
    folder = os.path.join("input", "16x16", "basic")
    os.makedirs(folder, exist_ok=True)
    for i in range(1, num + 1):
        file_path = os.path.join(folder, f"basic_{i}.txt")
        tasks.append((1, n, br, bc, file_path))

    results = []
    total_tasks = len(tasks)
    print(f"Total tasks: {total_tasks}")

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(generate_testcase, task) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            try:
                res = future.result()
                print(res)
                results.append(res)
            except Exception as exc:
                print(f"Task generated an exception: {exc}")
    return results


if __name__ == "__main__":
    create_test_cases(1000)
