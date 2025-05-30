
from Algorithms import First_Version_Venom, Second_Version_Venom, Latest_Version_Venom, Learning_Snake_Venom
from Algorithms import BFO, AStar, EBS_AStar, Dijkstra
from Utils.Metrics import time_algorithm
import os
import time
import argparse


parser = argparse.ArgumentParser(description="Snake Venom Algorithm")

parser.add_argument("-sp","--startpath",
                    default=os.path.dirname(os.path.abspath(__file__)),
                    help="The default value of start path is the current directory location of the script or main.py")

parser.add_argument("-tp", "--targetpath",
                    help="An absolute target path for the algorithm to find",
                    required=True)

parser.add_argument("-tf", "--targetfile",
                    help="A target file that must contain a valid filename along and its extension",
                    required=True)

parser.add_argument("-rt", "--runtime",
                    help="A run time in seconds for each algorithm to run",
                    type=float,
                    default=0)

parser.add_argument("-alg", "--algorithm",
                    help="An algorithm to run. The default value is all algorithms",
                    choices=["none","all", "SVT", "SVT_A", "SVT_B", "SVT_C", "A_Star", "Dijkstra", "BFO", "EBS"],
                    nargs="*",
                    metavar="algorithm",
                    default="all")


if __name__ == "__main__":
    # Parse arguments
    arguments = parser.parse_args()
    
    # Initialize constants with argument values or defaults
    STARTING_PATH = arguments.startpath
    TARGET_PATH = arguments.targetpath
    TARGET_FILE = arguments.targetfile
    RUN_TIME = arguments.runtime
    ALGOS = arguments.algorithm if isinstance(arguments.algorithm, list) else [arguments.algorithm]
    
    print(f"Starting path: {STARTING_PATH}")
    print(f"Target path: {TARGET_PATH}")
    print(f"Target file: {TARGET_FILE}")
    if RUN_TIME != 0:
        print(f"Run time: {RUN_TIME} {'minutes' if RUN_TIME > 1 else 'minute'}")
    print(f"Algorithms to run: {ALGOS}")

    file_Limits = [190_000, 200_000, 390_000, 400_000, 590_000, 600_000]

    # Initialize all algorithms
    algorithms = {
        "VIPER": First_Version_Venom.VIPER(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits),
        "MkI": Second_Version_Venom.VIPER_Mk_I(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits),
        "MkII": Latest_Version_Venom.VIPER_Mk_II(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits),
        "MkIII": Learning_Snake_Venom.VIPER_Mk_III(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits),
        "A_Star": AStar.AStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits),
        "EBS": EBS_AStar.EBSAStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits),
        "Dijkstra": Dijkstra.Dijkstra(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits),
        "BFO": BFO.BacterialForaging(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
    }

    # Set runtime if specified
    if RUN_TIME != 0:
        for algo in algorithms.values():
            algo.run_time_min = RUN_TIME

    # Prepare results storage
    results = {}
    infected_nodes = []
    infected_files = []
    algorithm_names = []

    # Run selected algorithms
    if "all" in ALGOS:
        algorithms_to_run = algorithms.keys()
    else:
        algorithms_to_run = [alg for alg in ALGOS if alg in algorithms]

    for algo_name in algorithms_to_run:
        print(f"\nStarting {algo_name}...")
        algo = algorithms[algo_name]
        
        # Determine which method to call based on algorithm
        if algo_name == "VIPER":
            method = algo.viper
        elif algo_name == "MkI":
            method = algo.mk_i
        elif algo_name == "MkII":
            method = algo.mk_ii
        elif algo_name == "MkIII":
            method = algo.mk_iii
        elif algo_name == "A_Star":
            method = algo.a_star
        elif algo_name == "EBS":
            method = algo.ebs_astar
        elif algo_name == "Dijkstra":
            method = algo.dijkstra
        elif algo_name == "BFO":
            method = algo.run
        
        # Time the algorithm
        timed_result = time_algorithm(method)
        results[algo_name] = timed_result
        
        # Store results
        infected_nodes.append(timed_result[1][3])
        infected_files.append(timed_result[1][4])
        algorithm_names.append(algo_name)
        
        print(f"Completed {algo_name}: {timed_result}")
        time.sleep(10)  # Cooldown between algorithms
