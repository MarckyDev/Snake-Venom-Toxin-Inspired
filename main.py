from multiprocessing.pool import RUN
from Algorithms import First_Version_Venom, Second_Version_Venom, Latest_Version_Venom, Learning_Snake_Venom
from Algorithms import BFO, AStar, EBS_AStar, Dijkstra
from Utils.Metrics import time_algorithm
import os
import time
import argparse
import threading

# parser = argparse.ArgumentParser(description="Snake Venom Algorithm")


# parser.add_argument("-sp","--startpath",
#                     default=os.path.dirname(os.path.abspath(__file__)),
#                     help="The default value of start path is the current directory location of the script or main.py")

# parser.add_argument("-tp", "--targetpath",
#                     help="An absolute target path for the algorithm to find",
#                     required=True)

# parser.add_argument("-tf", "--targetfile",
#                     help="A target file that must contain a valid filename along and its extension",
#                     required=True)

# parser.add_argument("-rt", "--runtime",
#                     help="A run time in seconds for each algorithm to run",
#                     type=int,
#                     default=0)


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
# # TARGET_FILE ="TARGET_FILE.txt"

# arguments = parser.parse_args()
# arguments._get_args()

# Validate required arguments and provide user-friendly feedback
# if not arguments.targetpath:
#     print("Error: The -tp/--targetpath argument is required.")
#     print("Usage: python main.py -tp <targetpath> -tf <targetfile>")
#     exit(1)

# if not arguments.targetfile:
#     print("Error: The -tf/--targetfile argument is required.")
#     print("Usage: python main.py -tp <targetpath> -tf <targetfile>")
#     exit(1)


if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    ending_directory = "C:\\Users\\Lenovo\\OneDrive\\Documents\\ViberDownloads"
    target_filename = "0-02-06-f03acf01bf5fc00d60834ed955209705006160278ddd3d08a4cf674413e69a33_efcb943cc33e0102.jpg"
    file_limits = [190_000, 200_000, 390_000, 400_000, 590_000, 600_000]
    
    ebsa_star_instance = EBS_AStar.EBS(current_directory, ending_directory, target_filename, file_limits)
    result = ebsa_star_instance.execute()
    if result:
        path, infected_files, infected_nodes = result
        print("Found path:", path)
        print("Infected files:", infected_files)
        print("Infected nodes:", infected_nodes)
    else:
        print("No path found or search stopped.")
# if __name__ == "__main__":
#     # Constants
#     STARTING_PATH = os.path.dirname(os.path.abspath(__file__))
#     TARGET_PATH = ""
#     TARGET_FILE = "main.py"
#     RUN_TIME = 0
    
#     if arguments.startpath:
#         STARTING_PATH = arguments.startpath
#         print(f"Current starting path is: {STARTING_PATH}")

#     if arguments.targetpath:
#         TARGET_PATH = arguments.targetpath
#         print(f"Current target path is: {TARGET_PATH}")

#     if arguments.targetfile:
#         TARGET_FILE = arguments.targetfile
#         print(f"Current target file is: {TARGET_FILE}")

#     if arguments.runtime:
#         if arguments.runtime != 0:
#             RUN_TIME = arguments.runtime
#             print(f"Current run time is: {RUN_TIME} {"minutes" if RUN_TIME > 1 else "minute"}")


#     file_Limits = [190_000, 200_000, 390_000, 400_000, 590_000, 600_000]

#     SNAKE_VENOM_FIRST = First_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
#     SNAKE_VENOM_SECOND = Second_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
#     SNAKE_VENOM_LATEST = Latest_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
#     SNAKE_VENOM_LEARNING = Learning_Snake_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)

#     BACTERIA = BFO.BacterialForaging(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
#     A_STAR = AStar.AStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
#     EBS = EBS_AStar.EBSAStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
#     DIJKSTRA = Dijkstra.Dijkstra(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)

#     if RUN_TIME != 0:
#         SNAKE_VENOM_FIRST.run_time_min = RUN_TIME
#         SNAKE_VENOM_SECOND.run_time_min = RUN_TIME
#         SNAKE_VENOM_LATEST.run_time_min = RUN_TIME
#         SNAKE_VENOM_LEARNING.run_time_min = RUN_TIME
#         A_STAR.run_time_min = RUN_TIME
#         EBS.run_time_min = RUN_TIME
#         DIJKSTRA.run_time_min = RUN_TIME
#         BACTERIA.run_time_min = RUN_TIME

#     print("Starting.. EBS A Star")
#     time.sleep(5)
#     ebs_results = time_algorithm(EBS.ebs_astar)

#     # print("Starting.. First Version of Snake Venom")
#     # time.sleep(5)
#     # first_svt = time_algorithm(SNAKE_VENOM_FIRST.svt_a)
    
#     # print("Starting.. Second Version of Snake Venom")
#     # time.sleep(5)
#     # second_svt = time_algorithm(SNAKE_VENOM_SECOND.svt_a)
    
#     # print("Starting.. Current Version of Snake Venom")
#     # time.sleep(5)
#     # latest_svt = time_algorithm(SNAKE_VENOM_LATEST.new_svt_a)
    
#     # print("Starting.. Memory Based Learning of Snake Venom")
#     # time.sleep(5)
#     # learning_svt = time_algorithm(SNAKE_VENOM_LEARNING.new_svt_a)
#     # #
#     # print("Starting.. A Star")
#     # time.sleep(5)
#     # a_results = time_algorithm(A_STAR.a_star)
    
#     # print("Starting.. Dijkstra")
#     # time.sleep(5)
#     # d_results = time_algorithm(DIJKSTRA.dijkstra)
    
#     # print("Starting.. BFO")
#     # time.sleep(5)
#     # b_results = time_algorithm(BACTERIA.run)



