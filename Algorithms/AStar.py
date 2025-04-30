import os
from os.path import normpath, abspath, samefile
from pathlib import Path
import threading
from datetime import datetime
import time
from Utils.FileProcessing import FileProcessing
from Utils.PathingUtil import reconstruct_path
from Utils.PathingUtil import file_limit_reached, timer
from Utils.Metrics import results_in_file


class AStar:
    def __init__(self, current_dir, ending_path, target_file, file_limit=None, run_time_min=0):
        self.file_limit = file_limit
        self.run_time_min = run_time_min
        self.logged_limits = []

        self.current_dir = current_dir
        self.ending_path = normpath(ending_path)
        self.target_file = target_file
        self.target_found = False

        self.infected_files = 0
        self.infected_nodes = 0

        self.open_set = set()
        self.closed_set = set()
        self.g_scores = {}  # Cost from start to node
        self.f_scores = {}  # Estimated total cost (g + h)
        self.parent_map = {}  # To reconstruct path

        # Timer-related attributes
        self.stop_event = threading.Event()
        self.start_time = time.perf_counter()

    def heuristic(self, current_dir, goal_dir):
        """Heuristic based solely on the difference in file counts"""
        try:
            current_count = FileProcessing().count_files_in_directory(current_dir)
            goal_count = FileProcessing().count_files_in_directory(goal_dir)
            return abs(current_count - goal_count)  # Absolute difference
        except:
            return float('inf')  # If inaccessible, treat as worst case

    def get_neighbors(self, node):
        """Get all accessible directories with file counts and status"""
        try:
            neighbors = FileProcessing().get_all_directories_with_file_counts(node)
            for neighbor in neighbors:
                neighbor["dir_name"] = normpath(abspath(neighbor["dir_name"]))
            return neighbors
        except PermissionError:
            print(f"Access denied to {node}. Skipping this directory.")
            return []
        except Exception as e:
            print(f"Error getting neighbors for {node}: {str(e)}")
            return []

    def process_neighbor(self, current, neighbor, goal):
        """Process a single neighbor node"""
        dir_name = neighbor["dir_name"]
        value = neighbor["value"]

        tentative_g_score = self.g_scores[current] + value

        if dir_name not in self.g_scores or tentative_g_score < self.g_scores[dir_name]:
            self.parent_map[dir_name] = current
            self.g_scores[dir_name] = tentative_g_score
            self.f_scores[dir_name] = tentative_g_score + self.heuristic(dir_name, goal)

            if dir_name not in self.open_set and dir_name not in self.closed_set:
                self.open_set.add(dir_name)

        try:
            for file in os.listdir(dir_name):
                file_path = os.path.join(dir_name, file)
                if os.path.isfile(file_path):
                    self.infected_files += 1
        except (PermissionError, FileNotFoundError):
            pass

    def a_star(self):
        """Optimized A* search algorithm with built-in timer"""
        current_dir = normpath(abspath(self.current_dir))
        goal_dir = normpath(abspath(self.ending_path))

        # Initialize data structures
        self.parent_map = {current_dir: None}
        self.g_scores[current_dir] = 0
        self.f_scores[current_dir] = self.heuristic(current_dir, goal_dir)
        self.open_set.add(current_dir)

        # Start timer thread if time limit is set
        timer_thread = None
        if self.run_time_min > 0:
            timer_thread = threading.Thread(target=timer, args=(self.start_time, self.run_time_min, self.stop_event))
            timer_thread.daemon = True
            timer_thread.start()

        if self.stop_event.is_set():
                print("Time limit reached. Stopping the process.")
                path = reconstruct_path(self.parent_map, current_dir, current_dir)
                print(f"Path: {path}")
                results_in_file(
                    path,
                    self.target_found,
                    time.perf_counter() - self.start_time,
                    self.infected_nodes,
                    self.infected_files,
                    "A_Star",
                    self.file_limit
                )
                return [
                    path,
                    self.target_found,
                    time.perf_counter() - self.start_time,
                    self.infected_nodes,
                    self.infected_files
                ]

        try:
            while self.open_set and not self.stop_event.is_set():
                current = min(self.open_set, key=lambda x: self.f_scores.get(x, float('inf')))
                self.open_set.remove(current)

                # Check file limit condition
                if self.file_limit:
                    for limit in self.file_limit:
                        if limit not in self.logged_limits and file_limit_reached(self.infected_files, limit):
                            self.logged_limits.append(limit)
                            path = reconstruct_path(self.parent_map, current_dir, current)

                            results_in_file(
                                path,
                                self.target_found,
                                time.perf_counter() - self.start_time,
                                self.infected_nodes,
                                self.infected_files,
                                "A_Star",
                                limit
                            )
                            break


                # Check target conditions
                try:
                    if samefile(current, goal_dir):
                        print(f"Reached target directory: {goal_dir}")
                        path = reconstruct_path(self.parent_map, current_dir, current)
                        self.target_found = True

                        results_in_file(
                            path,
                            self.target_found,
                            time.perf_counter() - self.start_time,
                            self.infected_nodes,
                            self.infected_files,
                            "A_Star",
                            self.file_limit
                        )

                        return path if path else [], self.infected_files, self.infected_nodes

                    if os.path.isdir(current) and self.target_file in os.listdir(current):
                        print(f"Found {self.target_file} in {current}!")
                        self.target_found = True
                        path = reconstruct_path(self.parent_map, current_dir, current)

                        results_in_file(
                            path,
                            self.target_found,
                            time.perf_counter() - self.start_time,
                            self.infected_nodes,
                            self.infected_files,
                            "A_Star",
                            self.file_limit
                        )

                        return path if path else [], self.infected_files, self.infected_nodes
                except (PermissionError, FileNotFoundError) as e:
                    print(f"Error checking directory {current}: {str(e)}")
                    continue

                self.closed_set.add(current)
                self.infected_nodes += 1

                # Process neighbors
                neighbors = self.get_neighbors(current)
                for neighbor in neighbors:
                    self.process_neighbor(current, neighbor, goal_dir)

                # Add parent directory as fallback
                parent_dir = normpath(abspath(os.path.dirname(current)))
                if parent_dir != current and parent_dir not in self.closed_set:
                    if parent_dir not in self.g_scores:
                        self.g_scores[parent_dir] = float('inf')

                    neighbor_data = {
                        "dir_name": parent_dir,
                        "value": 1,
                        "status": "normal"
                    }
                    self.process_neighbor(current, neighbor_data, goal_dir)
            path = reconstruct_path(self.parent_map, current_dir, current)
            return [path if path else [], self.infected_files, self.infected_nodes]
        finally:
            # Clean up timer thread
            if timer_thread and timer_thread.is_alive():
                self.stop_event.set()
                timer_thread.join()

