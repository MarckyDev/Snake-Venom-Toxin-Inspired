from Algorithms import AStar, EBS_AStar, Dijkstra, BFO, Learning_Snake_Venom, First_Version_Venom, Second_Version_Venom, Latest_Version_Venom
from Utils.Metrics import time_algorithm
import os
import time


def has(target_string: str, required_chars: str) -> bool:
    """Checks if the target string contains the required characters."""
    if required_chars in target_string:
        return True

    return False


# Constants
STARTING_PATH = os.path.dirname(os.path.abspath(__file__))

# TARGET_PATH = "C:\\Users\\goodb\\OneDrive\\Documents\\TARGET_DIR"
# TARGET_FILE = "target.txt"
# TARGET_PATH = "C:\\Users\\Lenovo\\OneDrive\\Documents\\ViberDownloads"
# TARGET_FILE = "0-02-06-f03acf01bf5fc00d60834ed955209705006160278ddd3d08a4cf674413e69a33_efcb943cc33e0102.jpg"

TARGET_PATH = "C:\\Users\\Lenovo\\Videos\\Twinmaker"
TARGET_FILE ="WIN_20250324_15_07_48_Pro.mp4"

# TARGET_PATH = "C:\\Users\\Lenovo\\OneDrive\\Desktop\\Programming\\MIPS ASM"
# TARGET_FILE ="maasim.asm"

# TARGET_PATH = "C:\\Users\\JiafeiMeifen\\Videos\\TARGET_DIR"
# TARGET_FILE ="TARGET_FILE.txt"

file_Limits = [30_000, 60_000, 100_000, 200_000]

SNAKE_VENOM_FIRST = First_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
SNAKE_VENOM_SECOND = Second_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
SNAKE_VENOM_LATEST = Latest_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
SNAKE_VENOM_LEARNING = Learning_Snake_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)

BFO = BFO.BacterialForaging(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
A_STAR = AStar.AStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
EBS_AStar = EBS_AStar.EBSAStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
DIJKSTRA = Dijkstra.Dijkstra(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)

# TOTAL_FILES = 0
# TOTAL_NODES = 0



if __name__ == "__main__":
    print("Starting.. EBS A Star")
    time.sleep(5)
    ebs_results = time_algorithm(EBS_AStar.ebs_astar)

    # print("Starting.. First Version of Snake Venom")
    # time.sleep(5)
    # first_svt = time_algorithm(SNAKE_VENOM_FIRST.svt_a)
    #
    # print("Starting.. Second Version of Snake Venom")
    # time.sleep(5)
    # second_svt = time_algorithm(SNAKE_VENOM_SECOND.svt_a)
    #
    # print("Starting.. Current Version of Snake Venom")
    # time.sleep(5)
    # latest_svt = time_algorithm(SNAKE_VENOM_LATEST.new_svt_a)
    #
    # print("Starting.. Memory Based Learning of Snake Venom")
    # time.sleep(5)
    # learning_svt = time_algorithm(SNAKE_VENOM_LEARNING.new_svt_a)
    #
    # print("Starting.. A Star")
    # time.sleep(5)
    # a_results = time_algorithm(A_STAR.a_star)
    #
    # print("Starting.. Dijkstra")
    # time.sleep(5)
    # d_results = time_algorithm(DIJKSTRA.dijkstra)
    #
    # print("Starting.. BFO")
    # time.sleep(5)
    # b_results = time_algorithm(BFO.run)

    # print(b_results)


