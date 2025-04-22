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


# Constants
STARTING_PATH = ""
TARGET_PATH = ""
TARGET_FILE = ""

file_Limits = [30_000, 60_000, 100_000, 200_000]

SNAKE_VENOM_FIRST = First_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
SNAKE_VENOM_SECOND = Second_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
SNAKE_VENOM_LATEST = Latest_Version_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
SNAKE_VENOM_LEARNING = Learning_Snake_Venom.SnakeVenom(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)

BFO = BFO.BacterialForaging(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
A_STAR = AStar.AStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
EBS_AStar = EBS_AStar.EBSAStar(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)
DIJKSTRA = Dijkstra.Dijkstra(STARTING_PATH, TARGET_PATH, TARGET_FILE, file_limit=file_Limits)



if __name__ == "__main__":
    print(arguments.startpath)
    if arguments.startpath:
        STARTING_PATH = arguments.startpath
        print(f"Current starting path is: {STARTING_PATH}")

    if arguments.targetpath:
        TARGET_PATH = arguments.targetpath
        print(f"Current target path is: {TARGET_PATH}")

    if arguments.targetfile:
        TARGET_FILE = arguments.targetfile
        print(f"Current target file is: {TARGET_FILE}")

    print("Starting.. EBS A Star")
    time.sleep(5)
    ebs_results = time_algorithm(EBS_AStar.ebs_astar)

    # print("Starting.. First Version of Snake Venom")
    # time.sleep(5)
    # first_svt = time_algorithm(SNAKE_VENOM_FIRST.svt_a)
    
    # print("Starting.. Second Version of Snake Venom")
    # time.sleep(5)
    # second_svt = time_algorithm(SNAKE_VENOM_SECOND.svt_a)
    
    # print("Starting.. Current Version of Snake Venom")
    # time.sleep(5)
    # latest_svt = time_algorithm(SNAKE_VENOM_LATEST.new_svt_a)
    
    # print("Starting.. Memory Based Learning of Snake Venom")
    # time.sleep(5)
    # learning_svt = time_algorithm(SNAKE_VENOM_LEARNING.new_svt_a)
    # #
    # print("Starting.. A Star")
    # time.sleep(5)
    # a_results = time_algorithm(A_STAR.a_star)
    
    # print("Starting.. Dijkstra")
    # time.sleep(5)
    # d_results = time_algorithm(DIJKSTRA.dijkstra)
    
    # print("Starting.. BFO")
    # time.sleep(5)
    # b_results = time_algorithm(BFO.run)

    # print(b_results)


