import time
from typing import Callable, Any
import inspect
from datetime import datetime

def exploitation_rate(infected_files: int,  total_files: int) -> float:
    return (infected_files / total_files) * 100

def speed_percent(algorithm_1_time: int, algorithm_2_time: int):
    if algorithm_1_time == 0:
        return 0
    return ((algorithm_1_time - algorithm_2_time) / algorithm_1_time) * 100

def reduction_rate(algorithm_1_visited_nodes: int, algorithm_2_visited_nodes: int) -> float:
    return (algorithm_1_visited_nodes / algorithm_2_visited_nodes) * 100

def visit_percent(algorithm_1_visited_nodes: int, total_nodes: int) -> float:
    return (algorithm_1_visited_nodes / total_nodes) * 100

def time_algorithm(algorithm: Callable[..., Any], starting_directory: str = None, seed: int = None) -> list[Any]:

    # Check function signature to determine the correct arguments
    sig = inspect.signature(algorithm)
    params = sig.parameters

    start = time.perf_counter()

    results = algorithm()

    end = time.perf_counter()
    elapsed = end - start

    return [elapsed, results]

def results_in_file(path, path_found, elapsed_time, infected_nodes, infected_files, algo_name, limits):
    string = f"""
            {limits} Results

            {algo_name}
            Time Recorded: {datetime.now()}
            Elapsed time: {elapsed_time}
            Path: {path}
            Path Length: {len(path) if path else 0}
            Path Found: {path_found}
            Infected Files: {infected_files}
            Infected Nodes: {infected_nodes}
            """
    try:
        print("Adding Something into the File...")
        with open(algo_name + ".txt", "x") as file:
            file.write(string)
    except FileExistsError:
        with open(algo_name + ".txt", "a") as file:
            file.write("\n\n" + string)

    print("Done making the File...")


'''
Metrics
> Power consumption
> Execution Time
> Path Costing
> Heuristic Accuracy
> Path Clearance
> Path Cost leg
> Sub-optimality ratio
> Success rate
> Exploration Efficiency
> Memory Usage
> Path Smoothness
> Equation Efficiency
'''