from multiprocessing.pool import RUN
from Algorithms import First_Version_Venom, Second_Version_Venom, Latest_Version_Venom, Learning_Snake_Venom
from Algorithms import BFO, AStar, EBS_AStar, Dijkstra
from Utils.Metrics import time_algorithm
import os
import time
import argparse
import threading

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

# parser.add_argument("-f", "--filelimit",
#                     help="A file limit for the algorithm to run. The default value is 200000",
#                     choices=["all", "first_svt", "second_svt", "latest_svt", "learning_svt", "a_star", "dijkstra", "bfo"],
#                     nargs="*",
#                     metavar="algorithm",
#                     default="all")

parser.add_argument("-rt", "--runtime",
                    help="A run time in seconds for each algorithm to run",
                    type=float,
                    default=0)

parser.add_argument("-alg", "--algorithm",
                    help="An algorithm to run. The default value is all algorithms",
                    choices=["all", "SVT", "SVT_A", "SVT_B", "SVT_C", "A_Star", "Dijkstra", "BFO", "EBS"],
                    nargs="*",
                    metavar="algorithm",
                    default="all")


def has(target_string: str, required_chars: str) -> bool:
    """Checks if the target string contains the required characters."""
    if required_chars in target_string:
        return True

    return False




# TARGET_PATH = "C:\\Users\\goodb\\OneDrive\\Documents\\TARGET_DIR"
# TARGET_FILE = "target.txt"
# TARGET_PATH = "C:\\Users\\Lenovo\\OneDrive\\Documents\\ViberDownloads"
# TARGET_FILE = "0-02-06-f03acf01bf5fc00d60834ed955209705006160278ddd3d08a4cf674413e69a33_efcb943cc33e0102.jpg"

# TARGET_PATH = "C:\\Users\\Lenovo\\OneDrive\\Desktop\\Programming\\MIPS ASM"
# TARGET_FILE ="maasim.asm"

# TARGET_PATH = "C:\\Users\\JiafeiMeifen\\Videos\\TARGET_DIR"
# TARGET_FILE ="TARGET_FILE.txt"

arguments = parser.parse_args()
arguments._get_args()

if __name__ == "__main__":
    # Constants
    STARTING_PATH = os.path.dirname(os.path.abspath(__file__))
    TARGET_PATH = os.path.dirname(os.path.abspath(__file__))
    TARGET_FILE = "main.py"
    RUN_TIME = 0
    ALGOS = ["all"]
    
    if arguments.startpath:
        STARTING_PATH = arguments.startpath
        print(f"Current starting path is: {STARTING_PATH}")

    if arguments.targetpath:
        TARGET_PATH = arguments.targetpath
        print(f"Current target path is: {TARGET_PATH}")

    if arguments.targetfile:
        TARGET_FILE = arguments.targetfile
        print(f"Current target file is: {TARGET_FILE}")

    if arguments.runtime:
        if arguments.runtime != 0:
            RUN_TIME = arguments.runtime
            print(f"Current run time is: {RUN_TIME} {"minutes" if RUN_TIME > 1 else "minute"}")
    
    if arguments.algorithm:
        if arguments.algorithm != "all":
            ALGOS = arguments.algorithm
            print(f"Current algorithms are: {ALGOS}")


    file_Limits = [190_000, 200_000, 390_000, 400_000, 590_000, 600_000]

    SNAKE_VENOM_FIRST = First_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
    SNAKE_VENOM_SECOND = Second_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
    SNAKE_VENOM_LATEST = Latest_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
    SNAKE_VENOM_LEARNING = Learning_Snake_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)

    BACTERIA = BFO.BacterialForaging(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
    A_STAR = AStar.AStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
    EBS = EBS_AStar.EBSAStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
    DIJKSTRA = Dijkstra.Dijkstra(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)

    if RUN_TIME != 0:
        SNAKE_VENOM_FIRST.run_time_min = RUN_TIME
        SNAKE_VENOM_SECOND.run_time_min = RUN_TIME
        SNAKE_VENOM_LATEST.run_time_min = RUN_TIME
        SNAKE_VENOM_LEARNING.run_time_min = RUN_TIME
        A_STAR.run_time_min = RUN_TIME
        EBS.run_time_min = RUN_TIME
        DIJKSTRA.run_time_min = RUN_TIME
        BACTERIA.run_time_min = RUN_TIME

    import matplotlib.pyplot as plt
    import numpy as np


    infected_nodes = []
    infected_files = []

    for algo in ALGOS:
        match algo:
            case "SVT":
                print("Starting.. First Version of Snake Venom (SVT-Vanilla)")
                SNAKE_VENOM_FIRST.run_time_min = RUN_TIME
                first_svt = time_algorithm(SNAKE_VENOM_FIRST.svt_a)

                infected_files.append(first_svt[1][4])
                infected_nodes.append(first_svt[1][3])
                time.sleep(10)
            case "SVT_A":
                print("Starting.. Second Version of Snake Venom (SVT-A)")
                SNAKE_VENOM_SECOND.run_time_min = RUN_TIME
                second_svt = time_algorithm(SNAKE_VENOM_SECOND.svt_a)

                infected_files.append(second_svt[1][4])
                infected_nodes.append(second_svt[1][3])
                time.sleep(10)
            case "SVT_B":
                print("Starting.. Current Version of Snake Venom (SVT - B)")
                SNAKE_VENOM_LATEST.run_time_min = RUN_TIME
                latest_svt = time_algorithm(SNAKE_VENOM_LATEST.new_svt_a)

                infected_files.append(latest_svt[1][4])
                infected_nodes.append(latest_svt[1][3])
                time.sleep(10)
            case "SVT_C":
                print("Starting.. Memory Based Learning of Snake Venom (SVT - C)")
                SNAKE_VENOM_LEARNING.run_time_min = RUN_TIME
                learning_svt = time_algorithm(SNAKE_VENOM_LEARNING.new_svt_a)

                infected_files.append(learning_svt[1][4])
                infected_nodes.append(learning_svt[1][3])
                time.sleep(10)
            case "A_Star":
                print("Starting.. A Star")
                A_STAR.run_time_min = RUN_TIME
                a_results = time_algorithm(A_STAR.a_star)

                infected_files.append(a_results[1][4])
                infected_nodes.append(a_results[1][3])
                time.sleep(10)
            case "Dijkstra":
                print("Starting.. Dijkstra")
                DIJKSTRA.run_time_min = RUN_TIME
                d_results = time_algorithm(DIJKSTRA.dijkstra)

                infected_files.append(d_results[1][4])
                infected_nodes.append(d_results[1][3])
                time.sleep(10)
            case "BFO":
                print("Starting.. BFO")
                BACTERIA.run_time_min = RUN_TIME
                b_results = time_algorithm(BACTERIA.run)

                infected_files.append(b_results[1][4])
                infected_nodes.append(b_results[1][3])
                time.sleep(10)
            case "EBS":
                print("Starting.. EBS A Star")
                EBS.run_time_min = RUN_TIME
                ebs_results = time_algorithm(EBS.ebs_astar)

                infected_files.append(ebs_results[1][4])
                infected_nodes.append(ebs_results[1][3])
                time.sleep(10)
            case "all":
                print("Starting.. EBS A Star")
                time.sleep(10)
                ebs_results = time_algorithm(EBS.ebs_astar)

                print("Starting.. First Version of Snake Venom")
                time.sleep(10)
                first_svt = time_algorithm(SNAKE_VENOM_FIRST.svt_a)
                
                print("Starting.. Second Version of Snake Venom")
                time.sleep(10)
                second_svt = time_algorithm(SNAKE_VENOM_SECOND.svt_a)
                
                print("Starting.. Current Version of Snake Venom")
                time.sleep(10)
                latest_svt = time_algorithm(SNAKE_VENOM_LATEST.new_svt_a)
                
                print("Starting.. Memory Based Learning of Snake Venom")
                time.sleep(10)
                learning_svt = time_algorithm(SNAKE_VENOM_LEARNING.new_svt_a)
                #
                print("Starting.. A Star")
                time.sleep(10)
                a_results = time_algorithm(A_STAR.a_star)
                
                print("Starting.. Dijkstra")
                time.sleep(10)
                d_results = time_algorithm(DIJKSTRA.dijkstra)
                
                print("Starting.. BFO")
                time.sleep(10)
                b_results = time_algorithm(BACTERIA.run)
                

                infected_files.append(first_svt[1][4])
                infected_nodes.append(first_svt[1][3])
                infected_files.append(second_svt[1][4])
                infected_nodes.append(second_svt[1][3])
                infected_files.append(latest_svt[1][4])
                infected_nodes.append(latest_svt[1][3])
                infected_files.append(learning_svt[1][4])
                infected_nodes.append(learning_svt[1][3])
                infected_files.append(a_results[1][4])
                infected_nodes.append(a_results[1][3])
                infected_files.append(d_results[1][4])
                infected_nodes.append(d_results[1][3])
                infected_files.append(ebs_results[1][4])
                infected_nodes.append(ebs_results[1][3])
                infected_files.append(b_results[1][4])
                infected_nodes.append(b_results[1][3])
                
            case _:
                print("Invalid algorithm specified. Please choose from the available algorithms.")
                continue
        


    plt.bar(ALGOS, infected_files, width=0.3)
    plt.title('Infected Files of the Algorithms in a set time')
    plt.xlabel('Algorithms')
    plt.ylabel('Infected Files')
    plt.show()


    plt.bar(ALGOS, infected_nodes, width=0.3)
    plt.title('Infected Files of the Algorithms in a set time')
    plt.xlabel('Algorithms')
    plt.ylabel('Infected Nodes')
    plt.show()