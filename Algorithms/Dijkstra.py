import os
from os.path import normpath
import threading
import datetime
import time
from Utils.FileProcessing import FileProcessing
from Utils.PathingUtil import reconstruct_path, file_limit_reached, timer
from Utils.Metrics import results_in_file


class Dijkstra:
    def __init__(self, current_dir, ending_path, target_file, file_limit=None, run_time_min=0):

        self.file_limit = file_limit
        self.run_time_min = run_time_min
        self.logged_limits = []

        self.infected_files = 0
        self.infected_nodes = 0

        self.current_dir = current_dir
        self.target_file = target_file
        self.ending_path = normpath(ending_path)
        self.parent_map = {self.current_dir: None}
        self.current = None
        self.target_found = False

        # Timer-related attributes
        self.stop_event = threading.Event()
        self.start_time = time.perf_counter()

    def dijkstra(self):
        """Dijkstra's algorithm implementation with built-in timer"""
        current_dir = normpath(self.current_dir)
        self.current = current_dir

        # Start timer thread if time limit is set
        timer_thread = None
        if self.run_time_min > 0:
            timer_thread = threading.Thread(target=timer, args=(self.start_time, self.run_time_min, self.stop_event))
            timer_thread.daemon = True
            timer_thread.start()

        if self.stop_event.is_set():
            print("Time limit reached. Stopping the process.")
            path = reconstruct_path(self.parent_map, self.current_dir, current_dir)
            print(f"Path: {path}")
            results_in_file(
                path,
                self.target_found,
                time.perf_counter() - self.start_time,
                self.infected_nodes,
                self.infected_files,
                "Dijkstra",
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
            # Initialize data structures
            distances = {current_dir: 0}  # Cost from start to node
            visited = set()
            unvisited = {current_dir}

            while unvisited and not self.stop_event.is_set():
                # Get node with smallest distance
                current = min(unvisited, key=lambda x: distances.get(x, float('inf')))
                self.current = current
                unvisited.remove(current)

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
                                "Dijkstra",
                                limit)

                            break

                # Skip if already visited
                if current in visited:
                    continue

                visited.add(current)
                self.infected_nodes += 1

                # Check if target file is found
                try:
                    if self.target_file in os.listdir(current):
                        path = reconstruct_path(self.parent_map, current_dir, current)
                        self.target_found = True

                        results_in_file(
                            path,
                            self.target_found,
                            time.perf_counter() - self.start_time,
                            self.infected_nodes,
                            self.infected_files,
                            "Dijkstra",
                            self.file_limit)

                        return path, self.infected_files, self.infected_nodes
                except PermissionError:
                    continue

                # Get neighbors (subdirectories)
                try:
                    neighbors = FileProcessing().get_all_directories_with_file_counts(current)
                except PermissionError:
                    continue

                for neighbor in neighbors:
                    dir_name = normpath(neighbor["dir_name"])
                    value = neighbor["value"]

                    # Calculate new distance
                    new_distance = distances[current] + value

                    # Update if we found a shorter path
                    if dir_name not in distances or new_distance < distances[dir_name]:
                        distances[dir_name] = new_distance
                        self.parent_map[dir_name] = current
                        unvisited.add(dir_name)

                    # Count files in this directory
                    try:
                        for file in os.listdir(dir_name):
                            file_path = os.path.join(dir_name, file)
                            if os.path.isfile(file_path):
                                self.infected_files += 1
                    except PermissionError:
                        continue

                # Add parent directory as fallback
                parent_dir = normpath(os.path.dirname(current))
                if parent_dir != current and parent_dir not in self.parent_map:
                    self.parent_map[parent_dir] = current
                    unvisited.add(parent_dir)
                    distances[parent_dir] = distances[current] + 1  # Standard cost for parent traversal

        finally:
            # Clean up timer thread
            if timer_thread and timer_thread.is_alive():
                self.stop_event.set()
                timer_thread.join()

            # If target not found, return path to last visited directory
            return [reconstruct_path(self.parent_map, current_dir, self.current), self.infected_files, self.infected_nodes]